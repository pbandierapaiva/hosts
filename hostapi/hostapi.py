from fastapi import FastAPI, Request

from pydantic import BaseModel
from typing import Optional

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

import mariadb
import re

from conexao import conexao


app = FastAPI()


app.mount("/web", StaticFiles(directory="web"), name="web")

class DB:
	def __init__(self):
		self.con= mariadb.connect(**conexao)
		self.cursor= self.con.cursor(dictionary=True)
	def commit(self):
		self.con.commit()

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
	db.cursor.execute("Select id,nome,estado,tipo from maq where tipo!='V'")
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

class NetDev(BaseModel):
	ip: str
	rede: str
	ether: Optional[str]
	maq: int
	
class HostInfo(BaseModel):
	hostid:int
	nome: str
	estado: int
	tipo: str
	hospedeiro: Optional[int]
	so: Optional[str]
	kernel: Optional[str]
	
@app.get("/nets")
async def listaNets():
	db = DB()
	db.cursor.execute("Select * from rede")
	return JSONResponse(content=jsonable_encoder(db.cursor.fetchall()))


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
	
#@app.put("/hosts/{host_id}/nets/", response_model=NetDev)
#async def criaNetDev(item: NetDev):
#	return item

#    update_item_encoded = jsonable_encoder(item)
#    items[item_id] = update_item_encoded
#    return update_item_encoded
#@app.put("/net")
#async def host():
#	db = DB()

