from fastapi import FastAPI, Request

from pydantic import BaseModel
from typing import Optional

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

import mariadb
import re
import os
import subprocess

from conexao import conexao, rootpw
from paramiko.client import SSHClient, AutoAddPolicy


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
	comentario: str
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

@app.get("/hosts/{hostid}/powerstatus")
async def hostinfoPowerStatus(hostid):
	db = DB()

	db.cursor.execute("Select netdev.ip, maq.altsec from maq,netdev where maq.id=netdev.maq AND maq.id='"+hostid+"' AND netdev.rede='ipmi'")
	h = db.cursor.fetchone()

	if not h:
		o = {"hostid":hostid,"status":"ERRO", "msg":"Não encontrado no banco" }
		return JSONResponse(content=jsonable_encoder(o))
	ip = h["ip"]
	if h["altsec"]:
		executa = ['ipmitool','-c', '-I','lanplus','-H', ip, '-U', 'admin', '-P', h["altsec"],'power','status']
	else:
		executa = ['ipmitool','-c', '-I','lanplus','-H', ip, '-U', 'admin', '-P', rootpw,'power','status']

	output = subprocess.run(executa, capture_output=True, text=True		)

	o = {"hostid":hostid,"ip":ip}
	if output.returncode==1:
		o["status"]='ERRO'
		o["msg"]= output.stderr
	else:
		o["status"]='OK'
		mensagem = str(output.stdout).strip()
		o["msg"]= mensagem
		ultima = mensagem.split()[-1]
		if str(ultima)=='on':
			o["power"]= "1"
		else:
			o["power"]= "0"
	return JSONResponse(content=jsonable_encoder(o))

@app.put("/hosts/{hostid}/powerstatus/{estado}")
async def hostinfoPowerStatus(hostid,estado):
	db = DB()
	try:
		db.cursor.execute("UPDATE maq SET estado='%s' WHERE id=%s"%(estado,hostid))
		print("UPDATE maq SET estado='%s' WHERE id=%s"%(estado,hostid))
		db.commit()
	except:
		print("ERRO DE UPDATE")

@app.get("/busca/{nome}")
async def hostsearch(nome):
	db = DB()

	db.cursor.execute("Select * from maq where nome LIKE '%"+nome+"%'")
	hostlist = db.cursor.fetchall()
	if not hostlist:
		return None
	for h in hostlist:
		db.cursor.execute("Select rede,ip from netdev where maq='"+str(h['id'])+"'")
		interfaces = db.cursor.fetchall()
		h['redes'] = {}
		for iface in interfaces:
			h['redes'][iface["ip"]]=iface["rede"]

	return JSONResponse(content=jsonable_encoder(hostlist))

@app.get("/hosts/{hostid}")
async def hostinfoById(hostid):
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
	db.cursor.execute("Select id,nome,comentario,estado,tipo,cpu,n,mem from maq where tipo!='V'")
	tudo = db.cursor.fetchall()

	d = []
	for li in tudo:
		db.cursor.execute("Select rede,ip from netdev where maq='"+str(li['id'])+"'")
		interfaces = db.cursor.fetchall()

		li['redes'] = {}
		for iface in interfaces:
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
	try:
		client.connect(ip,username='root',password=rootpw)
	except Exception as ex:
		template = "An exception of type {0} occurred. Arguments:\n{1!r}"
		m = template.format(type(ex).__name__, ex.args)
		return JSONResponse(content=jsonable_encoder({'STATUS':'ERROR', 'MSG':m}))

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
	stdin, stdout, stderr = client.exec_command('virsh list --name --inactive')
	for l in stdout:
			if l.strip()=='': break
			off.append(l.strip())
	for l in stderr:
		err+=l
	other = list( set(all) - (set(on)|set(off)))
	return JSONResponse(content=jsonable_encoder({"on":on,"off":off, "all":all, "other":other, "STATUS":"OK", "MSG":err}))

# @app.get("/vmhosts/{ip}/cmd/{cmd}")
# async def executa(ip,cmd):
# 	client = SSHClient()
# 	client.set_missing_host_key_policy( AutoAddPolicy )
# 	client.load_system_host_keys()
# 	client.load_host_keys("/home/paiva/.ssh/known_hosts")
# 	client.connect(ip,username='root',password=rootpw)
# 	stdin, stdout, stderr = client.exec_command(cmd)
# 	return JSONResponse(content=jsonable_encoder({"out":stdout.read(),"error":stderr.read()}))

@app.get("/vmhosts/{ip}/release")
async def catrelease(ip):
	ret = {'so':'','kernel':'','status':'OK'}
	client = SSHClient()
	client.load_system_host_keys()
	client.load_host_keys("/home/paiva/.ssh/known_hosts")
	client.connect(ip,username='root',password=rootpw)
	ret['status']=""
	stdin, stdout, stderr = client.exec_command("cat /etc/system-release")
	try:
		ret['so'] = stdout.read()
	except:
		ret['status']+="SO: "+ str( stderr.read() )

	stdin, stdout, stderr = client.exec_command("uname -a")
	try:
		ret['kernel'] = stdout.read()   #.split(' ')[2]
	except:
		ret['status']+="Kernel " + str( stderr.read() )

	stdin, stdout, stderr = client.exec_command("grep 'model name' /proc/cpuinfo")
	try:
		li = stdout.readlines()

		ret["n"] = len(li)
		ret['cpu'] = li[0].split('\t: ')[1]
	except:
		ret['status']+="CPU " + str( stderr.read() )

	stdin, stdout, stderr = client.exec_command("free -h | grep Mem:")
	try:
		li = stdout.readline()
		ret["mem"] = " ".join(li.split()).split()[1]
	except:
		ret['status']+="CPU " + str( stderr.read() )



	return JSONResponse(content=jsonable_encoder(ret))

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

	# print(str(dir(db.cursor)))
	return JSONResponse(content=jsonable_encoder({'status':'OK'}))

@app.get("/hosts/{host_id}/vm")
async def getVMInfo(host_id):
	db = DB()
	db.cursor.execute("Select * from maq where hospedeiro='"+host_id+"'")
	h = db.cursor.fetchall()
	return JSONResponse(content=jsonable_encoder(h))

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

@app.post("/hosts/{host_id}/{status}")
async def estadoHost(host_id, status):
	if status not in ["on","off","other"]:
		return JSONResponse(content=jsonable_encoder({"STATUS":"ERROR","MSG":"Status not on or off"}))
	if status=="on":
		s="1"
	elif status=="off":
		s="0"
	else: s = "-1"
	sql = "UPDATE maq SET estado='%s' WHERE id=%s"%(s,host_id)
	db = DB()
	try:
		status = db.cursor.execute(sql)
		db.commit()
	except Exception as ex:
		return JSONResponse(content=jsonable_encoder({'STATUS':'ERROR', 'MSG':ex.args}))
	return JSONResponse(content=jsonable_encoder({"status":"OK"}))

@app.post("/hosts/{host_id}")
async def atualizaHost(item: HostInfo):

		setexpression = " SET nome='%s',comentario='%s', estado='%s', tipo='%s', so='%s', kernel='%s', cpu='%s', n=%d, mem=%d "%\
			(item.nome, item.comentario, item.estado, item.tipo, item.so, item.kernel, item.cpu, item.n, item.mem)

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
