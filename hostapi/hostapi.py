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
		self.cursor= self.con.cursor()

@app.get("/")
async def root():
	#return {"message": "Hello World"}
	html_content = open("static/host.html").read()
	return HTMLResponse(content=html_content)
@app.get("/hosts")
async def hosts():
	db = DB()
	db.cursor.execute("Select maq.id,maq.nome, maq.estado,maq.tipo, netdev.ip from maq,netdev where netdev.maq=maq.id and netdev.rede='ipmi'")
	tudo = db.cursor.fetchall()
	
	d = []
	for li in tudo:
		d.append({'id':li[0],'nome':li[1],'estado':li[2], 'tipo':li[3], 'ip':li[4]})
		
	
	
	return JSONResponse(content=jsonable_encoder(d))


