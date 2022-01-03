from fastapi import FastAPI, Request

from pydantic import BaseModel
from typing import Optional

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

import mariadb
import re

from conexao import conexao, rootpw
from paramiko.client import SSHClient


app = FastAPI()


app.mount("/web", StaticFiles(directory="web"), name="web")

class DB:
	def __init__(self):
		self.con= mariadb.connect(**conexao)
		self.cursor= self.con.cursor(dictionary=True)
	def commit(self):
		self.con.commit()

class NetDev(BaseModel):
	ip: str
	rede: str
	ether: Optional[str]
	maq: int

class HostInfo(BaseModel):
	hostid:Optional[int]
	nome: str
	estado: str
	tipo: Optional[str]
	hospedeiro: Optional[int]
	so: Optional[str]
	kernel: Optional[str]
	cpu: Optional[str]
	n: Optional[int]
	mem: Optional[int]


@app.get("/")
async def root():
	#return {"message": "Hello World"}
	html_content = open("static/host.html").read()
	return HTMLResponse(content=html_content)

@app.get("/hosts/{hostid}")
async def hostinfo(hostid):
	db = DB()

	db.cursor.execute("Select * from maq where id='"+hostid+"'")
	h = db.cursor.fetchone()

	if not h:
		return None

	db.cursor.execute("Select rede,ip from netdev where maq='"+str(h['id'])+"'")
	interfaces = db.cursor.fetchall()

	h['redes'] = {}
	for iface in interfaces:
		h['redes'][iface["ip"]]=iface["rede"]
	return JSONResponse(content=jsonable_encoder(h))

@app.get("/hosts")
async def host():
	db = DB()

	# somente Hosts que não são VMs 'V'
	db.cursor.execute("Select id,nome,estado,tipo,cpu,n,mem from maq where tipo!='V'")
	tudo = db.cursor.fetchall()

	d = []
	for li in tudo:
		db.cursor.execute("Select rede,ip from netdev where maq='"+str(li['id'])+"'")
		interfaces = db.cursor.fetchall()

		li['redes'] = {}
		for iface in interfaces:
			#li['redes'][iface["rede"]]=iface["ip"]
			li['redes'][iface["ip"]]=iface["rede"]
		d.append(li)
	return JSONResponse(content=jsonable_encoder(d))

@app.get("/nets")
async def listaNets():
	db = DB()
	db.cursor.execute("Select * from rede")
	return JSONResponse(content=jsonable_encoder(db.cursor.fetchall()))

@app.delete("/netdev/{ip}", status_code=204)
def delete_book(ip: str) -> None:
	cmddel = "DELETE FROM netdev WHERE ip='%s' "%(ip)
	db = DB()
	status = db.cursor.execute(cmddel)
	db.commit()

@app.get("/vmhosts/{ip}")
def vmhostlist(ip):
	client = SSHClient()
	client.load_system_host_keys()
	client.load_host_keys("/home/paiva/.ssh/known_hosts")
	client.connect(ip,username='root',password=rootpw)
	all=[]
	on=[]
	off=[]
	err=""
	stdin, stdout, stderr = client.exec_command('virsh list --name --all')
	for l in stdout:
			if l.strip()=='': break
			all.append(l.strip())
	for l in stderr:
		err+=l
	stdin, stdout, stderr = client.exec_command('virsh list --name')
	for l in stdout:
			if l.strip()=='': break
			on.append(l.strip())
	for l in stderr:
		err+=l
	stdin, stdout, stderr = client.exec_command('virsh list --name --state-shutoff')
	for l in stdout:
			if l.strip()=='': break
			off.append(l.strip())
	for l in stderr:
		err+=l
	return JSONResponse(content=jsonable_encoder({"on":on,"off":off, "all":all, "ERROR":err}))

@app.get("/vmhosts/{ip}/cmd/{cmd}")
async def executa(ip,cmd):
	client = SSHClient()
	client.load_system_host_keys()
	client.load_host_keys("/home/paiva/.ssh/known_hosts")
	client.connect(ip,username='root',password=rootpw)
	stdin, stdout, stderr = client.exec_command(cmd)
	return JSONResponse(content=jsonable_encoder({"out":stdout.read(),"error":stderr.read()}))

@app.get("/vmhosts/{ip}/release")
async def catrelease(ip):
	client = SSHClient()
	client.load_system_host_keys()
	client.load_host_keys("/home/paiva/.ssh/known_hosts")
	client.connect(ip,username='root',password=rootpw)
	stdin, stdout, stderr = client.exec_command("cat /etc/system-release")
	return JSONResponse(content=jsonable_encoder({"out":stdout.read(),"error":stderr.read()}))

@app.put("/netdev")
async def criaNetDev( nd: NetDev):

	ipValido = True
	if not re.findall("\d+\.\d+\.\d+\.\d+", nd.ip):
		ipValido=False
	else:
		for n in nd.ip.split('.'):
			try:
				if int(n)<0 or int(n)>254:
					ipValido=False
			except:
				ipValido=False
	if not ipValido:
		return JSONResponse(content=jsonable_encoder({'status':'ERROR: invalid address'}))
	cmdins = "INSERT INTO netdev (ip,ether,rede,maq) VALUES ('%s','%s','%s',%d)"%(nd.ip,nd.ether,nd.rede,nd.maq)
	db = DB()
	try:
		status = db.cursor.execute(cmdins)
		db.commit()
	except:
		return JSONResponse(content=jsonable_encoder({'status':'ERROR: duplicate IP'}))

	print(str(dir(db.cursor)))
	return JSONResponse(content=jsonable_encoder({'status':'OK'}))

@app.get("/vm/{host_id}/{nome_vm}")
async def getVM(nome_vm):
		db = DB()
		db.cursor.execute("Select * from maq where tipo='V' AND nome='"+nome_vm+"'")
		h = db.cursor.fetchone()
		if not h: return JSONResponse(content=jsonable_encoder({"status":False,"vm":nome_vm}))
		db.cursor.execute("Select rede,ip from netdev where maq='"+str(h['id'])+"'")
		interfaces = db.cursor.fetchall()
		h['status'] = True
		h['redes'] = {}
		for iface in interfaces:
			h['redes'][iface["ip"]]=iface["rede"]
		return JSONResponse(content=jsonable_encoder(h))

@app.put("/vm")
async def criaVM(i: HostInfo):
	inscmd =  "INSERT INTO maq (nome, estado, tipo, hospedeiro) VALUES ('%s','%s','%s','%s')"%(i.nome,i.estado,i.tipo,i.hospedeiro)
	db = DB()
	try:
		status = db.cursor.execute(inscmd)
		db.commit()
	except:
		return JSONResponse(content=jsonable_encoder({'status':'ERROR: inserting into database'}))
	return JSONResponse(content=jsonable_encoder({"data":i.hostid, "status":"OK"}))

@app.post("/hosts/{host_id}")
async def atualizaHost(item: HostInfo):

		setexpression = " SET nome='%s', estado='%s', tipo='%s', so='%s', kernel='%s', cpu='%s', n=%d, mem=%d "%\
			(item.nome, item.estado, item.tipo, item.so, item.kernel, item.cpu, item.n, item.mem)

		if item.hospedeiro:
			setexpression+= ", hospedeiro=%d"%(item.hospedeiro)
		cmdupd = "UPDATE maq  "+setexpression+"  WHERE id=%d"%(item.hostid)

		db = DB()
		try:
			status = db.cursor.execute(cmdupd)
			db.commit()
		except:
			return JSONResponse(content=jsonable_encoder({'status':'ERROR: updating database'}))
		return JSONResponse(content=jsonable_encoder({"data":item.hostid, "status":"OK"}))
