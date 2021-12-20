from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

import mariadb

from conexao import conexao


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class DB:
	def __init__(self):
		self.con= mariadb.connect(**conexao)
		self.cursor= self.con.cursor(dictionary=True)

@app.get("/")
async def root():
	#return {"message": "Hello World"}
	html_content = open("static/host.html").read()
	return HTMLResponse(content=html_content)

@app.get("/hosts/{hostid}")
async def host(hostid):
	db = DB()
	
	db.cursor.execute("Select * from maq where id='"+hostid+"'")
	tudo = db.cursor.fetchall()
	return JSONResponse(content=jsonable_encoder(tudo))

@app.get("/hosts")
async def host():
	db = DB()
		
	#db.cursor.execute(
	#	"Select maq.id,maq.nome, maq.estado,maq.tipo, netdev.ip   \
	#		from maq,netdev where netdev.maq=maq.id and netdev.rede='ipmi'")
	db.cursor.execute("Select maq.id,maq.nome, maq.estado,maq.tipo from maq")
	tudo = db.cursor.fetchall()
	
	d = []
	for li in tudo:
		db.cursor.execute("Select rede,ip from netdev where maq='"+str(li['id'])+"'")
		interfaces = db.cursor.fetchall()
		 
		li['redes'] = {}
		for iface in interfaces:
			li['redes'][iface["rede"]]=iface["ip"]
		d.append(li)
		#d.append({'id':li['id'],'nome':li['nome'],'estado':li[2], 'tipo':li[3], 'net':redes})
	return JSONResponse(content=jsonable_encoder(d))


