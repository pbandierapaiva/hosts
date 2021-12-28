from browser import document
from browser import html, ajax, alert, confirm

import json

class HostList(html.DIV):
	def __init__(self):
		html.DIV.__init__(self)
		ajax.get("http://localhost:8000/hosts", oncomplete=self.onLoadHosts)
		self.className = "w3-sidebar w3-light-grey w3-bar-block" 
		self.style={"width":"25%"}
		titulo = html.H3("Hosts <span class=\"w3-tiny\">usando Brython")
		titulo.className = "w3-bar-item"
		self <= titulo
	def onLoadHosts(self, req):	
		cssBotao = "w3-button w3-tiny w3-center w3-padding-small w3-border w3-round"
		for h in req.json:
			linhaHost = html.DIV()
			linhaHost.className = "w3-bar w3-block"
			
			botaoHost = html.A(h["nome"])
			botaoHost.className = cssBotao
			botaoHost.style = {"width":"40%"}
			botaoHost.target = "infoarea"
			botaoHost.bind("click", self.hostinfo)
			botaoHost.local = "/hosts/"+str(h["id"])
			
			botaoIpmi = html.A("IPMI")
			botaoIpmi.className = cssBotao
			botaoIpmi.target="_blank"

			for n in h["redes"]:
				if h["redes"][n] == "ipmi": 
					#botaoIpmi.href = "http://"+h["redes"]["ipmi"]
					botaoIpmi.href = "http://"+n
					break
			
			tagTipo = html.A()
			tagTipo.className = cssBotao
			tagTipo.style = {"width":"10%"}
			if h["tipo"]=="H":
				tagTipo.innerHTML = "H"
				tagTipo.classList.add("w3-blue")
			elif h["tipo"]=="S":
				tagTipo.innerHTML = "S"
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
			self <= linhaHost
	def hostinfo(self, ev):
		NodeInfo(ev.currentTarget.local)

class NodeInfo(html.DIV):
	def __init__(self, loc):
		html.DIV.__init__(self)
		self.hostid = int(loc.split('/')[-1])
		self.loc = loc	
		document["infoarea"].innerHTML=""
		document["infoarea"] <= self	
		self.carrega()
	def carrega(self):
		ajax.get(self.loc, oncomplete=self.onLoadInfo)
		self.clear()

	def onLoadInfo(self, req):
		campos = req.json
		
		tit = document["hititle"]
		tit.innerHTML = "Host info: "+campos["nome"]

		form = html.FORM()
		form.className = "w3-container"

		form.appendChild(html.LABEL("Nome"), name="nome")
		self.nome = html.INPUT()
		self.nome.value = campos["nome"]
		self.nome.className = "w3-input w3-border"
		self.nome.disabled = True
		form.appendChild(self.nome)
		
		linhaEstadoTipo = html.TR()
		linhaEstadoTipo <= html.TD(html.LABEL("<p>Estado</p>"))
		
		tdEstado = html.TD()
		self.estadoON = html.INPUT(name='restado', value="1")
		self.estadoON.type = "radio"
		self.estadoON.className = "w3-radio"
		self.estadoON.disabled = True
		if( campos["estado"]=="1" ):  self.estadoON.checked = True
		tdEstado.appendChild(self.estadoON)
		tdEstado.appendChild(html.LABEL("ON<br>"))
		
		cpo2pb =  html.P()	
		self.estadoOFF = html.INPUT(name='restado', value="0")
		self.estadoOFF.type = "radio"
		if( campos["estado"]=="0" ): self.estadoOFF.checked = True
		self.estadoOFF.className = "w3-radio"
		self.estadoOFF.disabled = True
		tdEstado.appendChild(self.estadoOFF)
		tdEstado.appendChild(html.LABEL("OFF"))
		linhaEstadoTipo <= tdEstado

		self.tipo = html.TD()
		self.tipo.classList = "w3-tag w3-margin w3-padding"
		self.tipo.style = {"width":"200px"}
		self.tipo.disabled = True
		if campos["tipo"]=="H":  # HOST
			self.tipo.innerHTML = "Host"
			self.tipo.classList.add("w3-green") 
		elif campos["tipo"]=="S":  # Standalone
			self.tipo.innerHTML = "Standalone"
			self.tipo.classList.add("w3-teal")
		elif campos["tipo"]=="V":  # Máq. virtual
			self.tipo.innerHTML = "VM"		
			self.tipo.classList.add("w3-blue")
		else:  # Desconhecido
			self.tipo.innerHTML = "desconhecido"
			self.tipo.classList.add("w3-grey")
		linhaEstadoTipo.appendChild(self.tipo)

		tabEstadoTipo = html.TABLE()
		tabEstadoTipo.style = {"width":"100%"}
		tabEstadoTipo.appendChild(linhaEstadoTipo)
		form.appendChild(tabEstadoTipo)
		
		form.appendChild(html.LABEL("Sistema operacional")) 
		self.cposo = html.INPUT(name="so")
		self.cposo.value = campos["so"]
		self.cposo.className = "w3-input w3-border"
		self.cposo.disabled = True
		form.appendChild(self.cposo)

		form.appendChild(html.LABEL("Kernel"))
		self.cpokern = html.INPUT(name="kernel")
		self.cpokern.value = campos["kernel"]
		self.cpokern.className = "w3-input w3-border"
		self.cpokern.disabled = True
		form.appendChild(self.cpokern)
		
		self.listaInt = ListaInterfaces( self.loc, campos["redes"] )
		form <= self.listaInt 
		
		self.editBtn = html.DIV("Editar")
		self.editBtn.className = "w3-button w3-border w3-margin"
		self.editBtn.unbind("click")
		self.editBtn.bind("click", self.editar)		
		self.editBtn.style = {"display":"block"}
		self.cancelBtn = html.DIV("Cancelar")
		self.cancelBtn.className = "w3-button w3-border w3-margin"
		self.cancelBtn.bind("click", self.cancelar)
		self.cancelBtn.style = {"display":"none"}
		form.append(self.editBtn)
		form.append(self.cancelBtn)

		self.appendChild(form)
	def editar(self, ev):
		self.nome.disabled = False
		self.estadoON.disabled = False
		self.estadoOFF.disabled = False
		self.tipo.disabled = False
		self.cposo.disabled = False
		self.cpokern.disabled = False
		self.listaInt.enableEdit()
		self.editBtn.innerHTML = "Salvar"
		self.editBtn.unbind("click")
		self.editBtn.bind("click", self.salvar)		
		self.cancelBtn.style = {"display":"block"}
	def salvar(self, ev):
		alert("salvando ")
		document["infoarea"].innerHTML =  str(dir(self.cposo))
	def cancelar(self, ev):
		self.carrega()

class ListaInterfaces(html.DIV):
	def __init__(self, loc, dicInt):
		html.DIV.__init__(self)
		self <= html.LABEL("Interfaces:")
		self.interfaces = dicInt
		self.loc = loc
		# carrega cores das redes 
		ajax.get("http://localhost:8000/nets/", oncomplete=self.onLoadNets)
	def onLoadNets(self,req):
		redesCores = req.json
		dredesCor={}
		for r in redesCores:
			dredesCor[r["nome"]] = r["cor"]
		for ip in self.interfaces:
			self <= html.BR()
			tag = html.DIV()
			tag.classList = "w3-tag"
			tag.style ={"width":"120px"}
			tag.innerHTML = ip
			tag.bind("click",self.netdevRemove)
			tag.classList.add(dredesCor[  self.interfaces[ip]  ])
			self <= tag
			
		self.novoDev = html.DIV("+", id="buttonAddNet")
		self.novoDev.bind("click", self.novoNetDev )
		self.novoDev.className = "w3-tag w3-white"  #"w3-dropdown-click w3-badge w3-tiny w3-ripple w3-white w3-border"
		self.novoDev.style = {"display":"none", "width":"120px"}
		self <= self.novoDev		
	def novoNetDev(self, ev):
		AddNet(self.loc)
	def enableEdit(self):
		self.novoDev.style = {"display":"block"}	
	def netdevRemove(self, ev):
		confirm("Removendo"+str(ev.currentTarget.innerHTML))
		
class AddNet(html.DIV):
	def __init__(self,loc):
		html.DIV.__init__(self)
		self.loc = loc + "/net"
		self.maq = int(loc.split("/")[-1])
		document["dialog"] <= self
		self.className = "w3-modal"
		self.style.display = "block"  #"none"
		continente = html.DIV()
		continente.className = "w3-modal-content"
		caixa =  html.DIV()
		caixa.className = "w3-container w3-padding"
		fechaCaixa = html.SPAN("&times")
		fechaCaixa.className="w3-button w3-display-topright"
		fechaCaixa.bind("click", self.fecha)
		caixa <= html.H3("Adicionando interface de rede")
		caixa <= fechaCaixa
		caixa <= html.LABEL("Rede")
		self.rede=SelectNet()
		caixa <= self.rede
		caixa <= html.LABEL("Endereço IP")
		self.ip = html.INPUT()
		self.ip.className = "w3-input w3-border"
		caixa <= self.ip
		
		caixa <= html.LABEL("Ethernet")
		self.ether = html.INPUT()
		self.ether.className = "w3-input w3-border"
		caixa <= self.ether		
		ok = html.BUTTON("OK")
		ok.className = "w3-button w3-margin w3-border w3-round"
		ok.bind("click", self.confirma)

		caixa <= ok
		continente <= caixa
		self <=continente
	def confirma(self,ev):
		self.style.display = "none"
		d = {"ip":self.ip.value, "rede":self.rede.selecionado(), 
			"maq":self.maq, "ether":self.ether.value }
		alert(str(d))
		ajax.put("/netdev", data=json.dumps(d), oncomplete=self.added, headers={"Content-Type": "application/json; charset=utf-8"})
	def added(self, req):
		document["infoarea"].innerHTML= str(req.json)
	def show(self):
		self.style.display = "block"
	def fecha(self, ev):
		self.style.display = "none"
	

class SelectNet(html.SELECT):
	def __init__(self):
		html.SELECT.__init__(self)
		self.className = "w3-input w3-border"
		ajax.get("http://localhost:8000/nets/", oncomplete=self.onLoadNets)
	def onLoadNets(self,req):
		redes = req.json
		for r in redes:
			self <= html.OPTION(r["nome"]+" - "+ r["cidr"], value=r["nome"]	)
	def selecionado(self):
		return self.selectedOptions.item(0).value


# Coloca lista de Hosts na área
document["listahost"] <= HostList()




