from browser import document
from browser import html, ajax, alert

def onLoadHosts(req):
	listaH = document["infoarea"]
	listaH <= html.P("JSON")
	
	d = req.json
	listaH <= html.P(str(type(d)))

	listaH <= html.P("TEXT")	
	listaH <= html.P(req.text)

# Carrega lista de hosts
ajax.get("http://localhost:8000/hosts", oncomplete=onLoadHosts)





