from browser import document
from browser import html, ajax, alert, confirm

from browser.widgets.dialog import InfoDialog, Dialog

import json

class HostList(html.DIV):
	def __init__(self):
		html.DIV.__init__(self)
		ajax.get("http://localhost:8000/hosts", oncomplete=self.onLoadHosts)
		self.className = "w3-sidebar w3-light-grey w3-bar-block"
		self.style={"width":"25%"}
		titulo = html.H3("Hosts <span class=\"w3-tiny\">usando Brython!!!")
		titulo.className = "w3-bar-item"
		self <= titulo

		vmButton = html.DIV("VM Hosts")
		vmButton.className = "w3-bar-item"
		vmButton.bind("click",self.vmlist)
		self <= vmButton
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
					botaoIpmi.href = "http://"+n
					break

			tagTipo = html.A()
			tagTipo.className = cssBotao
			tagTipo.style = {"width":"10%"}
			if h["tipo"]=="H":
				tagTipo.innerHTML = "H"
				tagTipo.classList.add("w3-blue")
				tagTipo.bind("click",self.vmstate)
				tagTipo.ip = ""
				for n in h["redes"]:
					if h["redes"][n] != "ipmi":
						tagTipo.ip = n
				tagTipo.hostid = h["id"]
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
	def vmlist(self,ev):
		document["infoarea"].innerHTML=""
		document["infoarea"] <= VMHostList()
	def vmstate(self,ev):
		document["infoarea"].innerHTML=""
		document["infoarea"] <= EstadoVM(ev.currentTarget.hostid, ev.currentTarget.ip)

class VMHostList(html.DIV):
	def __init__(self):
		html.DIV.__init__(self)
		ajax.get("/hosts", oncomplete=self.onLoadHosts)

	def onLoadHosts(self, req):
		cssBotao = "w3-button w3-tiny w3-center w3-padding-small w3-border w3-round"
		for h in req.json:
			linhaHost = html.DIV()
			linhaHost.className = "w3-bar w3-block"
			if h["tipo"]!="H":
				next

			hostname = 	h["nome"]

			for n in h["redes"]:
				if h["redes"][n] != "ipmi":
					#botaoIpmi.href = "http://"+h["redes"]["ipmi"]
					#botaoIpmi.href = "http://"+n
					hostname += " root@"+n
					break
			self <= html.P(hostname)

class EntraTexto(html.DIV):
	def __init__(self, labelStr, valor="", width=""):
		html.DIV.__init__(self)
		if width !="":
			self.style = {"width":width}
		self.inputLbl = html.LABEL(labelStr)
		self.inputCpo = html.INPUT()
		self.inputCpo.value = valor
		self.inputCpo.className = "w3-input w3-border"
		self.inputCpo.disabled = True
		self.alterado = False
		self.inputCpo.bind("change", self.onChange)
		self <= self.inputLbl
		self <= self.inputCpo
	def enable(self):
		self.inputCpo.disabled = False
	def onChange(self,ev):
		self.alterado = True
	def valor(self):
		return self.inputCpo.value

class TipoHost(html.DIV):
	def __init__(self, tipo):
		html.DIV.__init__(self)
		self.classList = "w3-tag w3-margin w3-padding"
		self.style = {"width":"200px"}
		self.disabled = True
		self.tipo = tipo
		if self.tipo=="H":  # HOST
			self.innerHTML = "Host"
			self.classList.add("w3-green")
		elif self.tipo=="S":  # Standalone
			self.innerHTML = "Standalone"
			self.classList.add("w3-teal")
		elif self.tipo=="V":  # Máq. virtual
			self.innerHTML = "VM"
			self.classList.add("w3-blue")
		else:  # Desconhecido
			self.innerHTML = "desconhecido"
			self.classList.add("w3-grey")
	def valor(self):
		return self.tipo

class RadioEstado(html.DIV):
		def __init__(self, estado):
			html.DIV.__init__(self)
			self.estado = estado
			self.alterado = False
			self.estadoON = html.INPUT(name='restado', value="1",type = "radio", Class = "w3-radio")
			self.estadoON.disabled = True
			if( self.estado=="1" ):  self.estadoON.checked = True
			self <= self.estadoON
			self <= html.LABEL("ON<br>")
			self.estadoOFF = html.INPUT(name='restado', value="0", type = "radio", Class = "w3-radio")
			if( self.estado=="0" ): self.estadoOFF.checked = True
			self.estadoOFF.disabled = True
			self <=  self.estadoOFF
			self <= html.LABEL("OFF")
			self.estadoOFF.bind("change",self.onChange)
			self.estadoON.bind("change",self.onChange)
		def enable(self):
			self.estadoOFF.disabled = False
			self.estadoON.disabled = False
		def onChange(self, ev):
			self.alterado = True
		def valor(self):
			if self.estadoOFF.checked: return "0"
			if self.estadoON.checked: return "1"
			return None

class NodeInfoLine(html.DIV):
	def __init__(self, nid=None):
		html.DIV.__init__(self, Class="w3-card-4")
		
		if nid:	ajax.get("/hosts/"+str(nid),oncomplete=self.onHostInfoLoaded)
	def onHostInfoLoaded(self, response):
		resp = response.json
		alert(str(resp))
		
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
		form <= html.LABEL("<p>ID: "+str(campos["id"])+"</p>")

		self.nome = EntraTexto("Nome",campos["nome"])
		form <= self.nome
		self.cposo = EntraTexto("Sistema operacional",campos["so"])
		form <= self.cposo
		self.kernel = EntraTexto("Kernel",campos["kernel"])
		form <= self.kernel

		self.cpu = EntraTexto("Processador",campos["cpu"]) #, width="70%")
		self.n = EntraTexto("N",campos["n"]) #, width="30%")
		self.mem = EntraTexto("Memória",campos["mem"])  #, width="30%")
		cpulinha = html.TR()
		cpulinha <= html.TD(style={"width":"60%"}) <= self.cpu
		cpulinha <= html.TD(style={"width":"10%"}) <= self.n
		cpulinha <= html.TD(style={"width":"20%"}) <= self.mem
		form <= html.TABLE() <= cpulinha

		self.tipo = TipoHost(campos["tipo"])
		self.estado = RadioEstado(campos["estado"])

		linhaEstadoTipo = html.TR()
		linhaEstadoTipo <= html.TD(html.LABEL("<p>Estado</p>"))
		linhaEstadoTipo <= html.TD() <= self.estado
		linhaEstadoTipo <=  html.TD() <= self.tipo

		form <= html.TABLE() <= linhaEstadoTipo


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
		self.nome.enable()
		self.cposo.enable()
		self.kernel.enable()
		self.cpu.enable()
		self.n.enable()
		self.mem.enable()

		self.estado.enable()
		self.tipo.disabled = False
		self.listaInt.enableEdit()

		self.editBtn.innerHTML = "Salvar"
		self.editBtn.unbind("click")
		self.editBtn.bind("click", self.salvar)
		self.cancelBtn.style = {"display":"block"}
	def alterado(self):
		return self.nome.alterado or self.cposo.alterado or self.kernel.alterado or self.cpu.alterado or self.n.alterado or \
			self.mem.alterado or self.estado.alterado
	def salvar(self, ev):
		if not self.alterado():
			alert("Dados inalterados")
			self.carrega()
			return
		dados = {"hostid": self.hostid,
				"nome" :  self.nome.valor(),
				"so" : self.cposo.valor(),
				"estado" : self.estado.valor(),
				"tipo" : self.tipo.valor(),
				"kernel" : self.kernel.valor(),
				"cpu" : self.cpu.valor()
				}
		try:
				if	self.n.valor(): dados["n"] = int(self.n.valor())
				if	self.mem.valor(): dados["mem"] = int(self.mem.valor())
		except:
				alert("Valores de N e MEM devem ser inteiros")
				return
		ajax.post("/hosts/%d"%self.hostid, data=json.dumps(dados), oncomplete=self.added, headers={"Content-Type": "application/json; charset=utf-8"})
	def added(self,req):
		if req.json["status"]!="OK":
			alert("Erro de atualização de Host")
		self.carrega()
	def cancelar(self, ev):
		if self.alterado():
			if confirm("Descartar alterações?"):
				self.carrega()
		else:
			self.carrega()

class ListaInterfaces(html.DIV):
	def __init__(self, loc, dicInt):
		html.DIV.__init__(self)
		self <= html.LABEL("Interfaces:")
		self.interfaces = dicInt
		self.loc = loc
		# carrega cores das redes
		ajax.get("/nets/", oncomplete=self.onLoadNets)
	def onLoadNets(self,req):
		redesCores = req.json
		dredesCor={}
		for r in redesCores:
			dredesCor[r["nome"]] = r["cor"]
		self.ifaceTags = []
		self.ifaceDdowns = []
		for ip in self.interfaces:
			self <= html.BR()
			tag = html.BUTTON(Class = "w3-button")
			#tag.classList =  # w3-tag"
			tag.style ={"width":"120px"}   #,"cursor":"default"}
			tag.innerHTML = ip
			tag.classList.add(dredesCor[  self.interfaces[ip]  ])

			delif = html.A(Class="w3-bar-item w3-button")
			delif.innerHTML="Remover interface"
			delif.ip = ip
			delif.bind("click", self.netdevRemove)

			uname = html.A(Class="w3-bar-item w3-button")
			uname.innerHTML="uname"
			uname.ip = ip
			uname.bind("click", self.getUname)

			release = html.A(Class="w3-bar-item w3-button")
			release.innerHTML="Dist release"
			release.ip = ip
			release.bind("click", self.getRelease)

			dropdown =  html.DIV(Class="w3-dropdown-hover")
			dropdown <= tag
			dropdownitems = html.DIV(Class="w3-dropdown-content w3-bar-block w3-card-4")
			dropdownitems <= delif
			dropdownitems <= uname
			dropdownitems <= release
			dropdown <= dropdownitems
			dropdown.style = {"pointer-events": "none"}

			self <= dropdown
			self.ifaceTags.append(tag)
			self.ifaceDdowns.append(dropdown)

	def novoNetDev(self, ev):
		AddNet(self.loc)
	def enableEdit(self):
		novoDev = html.DIV("+")
		novoDev.bind("click", self.novoNetDev )
		novoDev.className = "w3-tag w3-white"
		novoDev.style = {"display":"block", "width":"120px","cursor":"pointer"}
		self <= novoDev
		for iDd in self.ifaceDdowns:
			iDd.style = {"pointer-events": "auto"}

	def netdevRemove(self, ev):
		if confirm("ATENÇÃO: Remover interface "+ev.currentTarget.ip+ "?"):
			ajax.delete("/netdev/%s"%(ev.currentTarget.innerHTML))
			InfoDialog("Status","Interface removida")
		document["infoarea"].innerHTML= ""
	def getUname(self,ev):
		ajax.get("/vmhosts/%s/cmd/uname -a"%ev.currentTarget.ip, oncomplete=self.dispUname)
	def dispUname(self,req):
		if req.json["error"]=="":
			alert(req.json["out"].split(' ')[2])
		else: alert(req.json["error"])
	def getRelease(self,ev):
		ajax.get("/vmhosts/%s/release"%ev.currentTarget.ip, oncomplete=self.dispRelease)
	def dispRelease(self,req):
		if req.json["error"]=="":
			alert(req.json["out"].strip())
		else: alert(req.json["error"])

class EstadoVM(html.DIV):
	def __init__(self,hostid,ip):
		html.DIV.__init__(self)
		
		
		
		self <= html.LABEL("VMs:")
		self.ip = ip
		self.hostid = hostid
		self.mensagem = html.P("Aguarde...")
		self <= self.mensagem
		ajax.get("/vmhosts/%s"%self.ip, oncomplete=self.onLoadVMs)
	def onLoadVMs(self,req):
		self.mensagem.hidden = true
		self.estado = req.json
		for vm in self.estado["all"]:
			ajax.get("/vm/"+str(self.hostid)+"/"+vm, oncomplete=self.vmLoaded)

	def vmLoaded(self,req):
		vm = req.json["vm"]
		if not req.json["status"]:
			alert("VM não encontrada, criando entrada no DB")
			d = {"nome":vm, "tipo":"V", "hospedeiro":self.hostid}
			if vm in self.estado["on"]: d["estado"]="1"
			elif vm in self.estado["off"]: d["estado"]="0"
			else: d["estado"]="-1"
			ajax.put("/vm/", data=json.dumps(d), oncomplete=self.vmAdded, headers={"Content-Type": "application/json; charset=utf-8"})

		it = html.P()
		bot = html.SPAN("&nbsp;")
		bot.className="w3-badge w3-tiny"
		if vm in self.estado["on"]:
			bot.classList.add("w3-green")
		elif vm in self.estado["off"]:
			bot.classList.add("w3-grey")
		else:
			bot.classList.add("w3-yellow")
		it <= bot
		it <= html.LABEL(vm)
		self <= it
		#self.mensagem.innerHTML= self.estado["ERROR"]
	def vmAdded(self, req):
		if req.json["status"]!="OK":
			alert(req.json["status"])

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
		ajax.put("/netdev", data=json.dumps(d), oncomplete=self.added, headers={"Content-Type": "application/json; charset=utf-8"})
	def added(self, req):
		if req.json["status"]=="OK":
			alert("Interface adicionada")
		else:
			alert(req.json["status"])
		#self.parentNode.parentNode.carrega()
		document["infoarea"].innerHTML= ""
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
