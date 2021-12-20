# Classes definido dados de rede, host e VM para transferir por  JSON
# Não foram utilizadas. Um banco de dados SQL foi utilizado para isso  -mais fácil


import json

class Net(dict):
	def __init__(self, netaddr, gw, vlan):
		dict.__init__(self)
		self['netaddr'] = netaddr
		self['gateway'] = gw
		self['vlan'] = vlan
		self['devs'] = []
	def addDev(self, ip, ether=None):
		self.devs.append(Netdev(ip,ether))
		
class Netdev(dict):
	def __init__(self, ip, ether=None):
		dict.__init__(self)
		self['ip']=ip
		self['ether']=ether
	
class Maquina(dict):
	def __init__(self, nome):
		dict.__init__(self)
		self['nome']=nome
		self['estado'] = 0 	# 0 off / 1 on
		self['so'] = ''
		self['netdev'] = []
	def addDev(self, nd):
		if type(nd)!=Netdev:
			raise TypeError
		self['netdev'].append(nd)
	def __str__(self):
		return json.dumps(self)

class Host(Maquina):
	def __init__(self, nome, tipo=None):
		Maquina.__init__(self,nome)
		self['tipo'] = tipo  	# S - standalone / H - host
		self['vms'] = []
		self['impi'] = None
	def addVM(self, vm):
		if type(vm)!=VM:
			raise TypeError
		self['vms'].append(vm)
		
class VM(Maquina):
	def __init__(self, nome):
		Maquina.__init__(self, nome)


class DC(dict):
	def __init__(self):
		dict.__init__(self)
		self['hosts'] = []
		self['nets'] = { 
			'ipmi':Net('10.90.8.0/24','10.90.8.1',998),
			'160':Net('172.22.160.0/22','172.22.160.1',164),
			'164':Net('172.22.164.0/22','172.22.164.1',111),
			'dmz':Net('200.144.92.128/26','200.144.93.129',4),
			'cloud':Net('10.100.0.0/24','10.100.0.1',1000),
			'core':Net('10.80.0.0/24','10.80.0.1',800),
			'fog':Net('10.99.9.0/24','10.99.9.1',999),
			'under':Net('10.90.0.0/24','10.90.0.1',900)
			}
	def addHost(self, h):
		if type(h)!=Host:
			raise TypeError
		for i in self['hosts']:
			if i['nome']==h['nome']:
				raise DuplicateName
		self['hosts'].append(h)
	def get(self, n):
		for h in self['hosts']:
			if n==h['nome']:
				return h
		return None

	def readCSV(self, fn):
		inf = open(fn)
		while True:
			li = inf.readline()
			if !li: break
			p = li.split(',')
			if p[0]=='': continue
			h = Host(p[6],p[1])
			d = NetDev(p[2])
			self['nets']['ipmi'].append(d)
			h['ipmi']=d
			 


		
from dc import *
d = DC()


def lixo:
	d.addHost(Host('teste3'))
	d.addHost(Host('teste2'))
	d.addHost(Host('teste1'))
	d
			
	d['hosts'][0].addVM(VM('vmt1h0'))		
	d['hosts'][0].addVM(VM('vmt2h0'))		
	d['hosts'][1].addVM(VM('vmt2h1'))			
