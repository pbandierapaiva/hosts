from browser import document
from browser import html, ajax, alert

def onLoadHosts(req):
	listaH = document["listahost"]
	listaH <= html.P("JSON")
	
	cssBotao = "w3-button w3-tiny w3-center w3-padding-small w3-border w3-round"
	for h in req.json:
		linhaHost = html.DIV()
		linhaHost.className = "w3-bar w3-block"
		
		botaoHost = html.A()
		botaoHost.className = cssBotao
		botaoHost.innerHTML = h["nome"]
		botaoHost.style = {"width":"40%"}
		botaoHost.target = "infoarea"
		botaoHost.onlick = hostinfo
		botaoHost.local = "/hosts/"+str(h["id"])
		
		botaoIpmi = html.A()
		botaoIpmi.className = cssBotao
		botaoIpmi.innerHTML = "IPMI"	
		botaoIpmi.target="_blank"
		botaoIpmi.href = "http://"+h["redes"]["ipmi"]
		
		tagTipo = html.A()
		tagTipo.className = cssBotao
		tagTipo.style = {"width":"10%"}
		if h["tipo"]=="H":
			tagTipo.innerHTML = "VM"
			tagTipo.classList.add("w3-blue")
		elif ["h.tipo"]=="S":
			tagTipo.innerHTML = "ST"
			tagTipo.classList.add("w3-teal")
		else:
			tagTipo.innerHTML = "??"
			tagTipo.classList.add("w3-grey")
		
		estadoHost = html.SPAN()
		estadoHost.innerHTML = "&nbsp;"
		estadoHost.className=cssBotao
		estadoHost.style = {"width":"3%"}
		if h["estado"]=="0": estadoHost.classList.add("w3-grey")
		elif h["estado"]=="1": estadoHost.classList.add("w3-green")
		else: estadoHost.classList.add("w3-yellow")

		linhaHost <= botaoHost
		linhaHost <= botaoIpmi
		linhaHost <= tagTipo
		linhaHost <= estadoHost
		listaH <= linhaHost
	
def hostinfo(ev):
	#const xhttp = new XMLHttpRequest();
	#xhttp.onload = onInfoHostLoaded;
	alert(ev.currentTarget.quem)
	#xhttp.open("GET", ev.currentTarget.quem);	
	#xhttp.send();
	

# Carrega lista de hosts
ajax.get("http://localhost:8000/hosts", oncomplete=onLoadHosts)





