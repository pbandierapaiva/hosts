#
# Conecta em todas as máquinas físicas marcadas como Host e resgata VMs e seus estados
#

import mariadb
import re
import os
import subprocess

from conexao import conexao, rootpw
from paramiko.client import SSHClient, AutoAddPolicy

class DB:
	def __init__(self):
		self.con= mariadb.connect(**conexao)
		self.cursor= self.con.cursor(dictionary=True)
	def commit(self):
		self.con.commit()

def allHosts():
	db = DB()

	# somente Hosts que não são VMs 'V'
	# db.cursor.execute("Select id,nome,estado,tipo,cpu,n,mem from maq where tipo!='V'")
	db.cursor.execute("Select id,nome,estado,tipo,cpu,n,mem from maq where tipo='H'")
	todoshostsdb = db.cursor.fetchall()

	contavm = 0

	d = []
	for li in todoshostsdb:
		hostOK = False

		hostid = li["id"]

		print("Host: %s (%d)"%(li["nome"],hostid))

		db.cursor.execute("Select netdev.ip, netdev.rede, maq.altsec, maq.estado from maq,netdev where maq.id=netdev.maq AND maq.id='%d'"%hostid)
		hosts = db.cursor.fetchall()

		# db.cursor.execute("Select rede,ip from netdev where maq='"+str(li['id'])+"'")
		# interfaces = db.cursor.fetchall()
		ipmi = ''
		li['redes'] = []
		# for iface in interfaces:
		for hostline in hosts:
			if hostline["rede"]=='ipmi':
				ipmi = hostline["ip"]
			li['redes'].append(hostline["ip"])

		if hostline["altsec"]:
			status = ipmiInfo(ipmi, hostline["altsec"])
		else: status = ipmiInfo(ipmi)

		if hostline["estado"]!=status:
			print("Status ALTERADO %s %s %s"%(hostline["nome"],hostid,status))
			updcmd = "UPDATE maq SET estado='%s'	WHERE id='%s'"%(status,hostid)
			# print(updcmd)
			try:
				status = db.cursor.execute(updcmd)
			except:
				input("Erro inserção BD >>"+updcmd)

			db.commit()

		if status!="1":
			continue
		# continue

		for ip in li['redes']:
			ret = hostinfo(ip,hostid)
			if ret['STATUS']=="OK":
				ipsucesso=ip
				hostOK=True
				break

		if not hostOK:
			print("Problemas com host: ",li)
			continue

		updcmd = """UPDATE maq SET cpu='%s', n=%d, mem='%s', kernel='%s', so='%s'
				WHERE id='%s'
		"""%(ret["cpu"],ret["n"],ret["mem"],ret["kernel"],ret["so"],hostid)

		try:
			# print("inserindo "+str(ret))
			status = db.cursor.execute(updcmd)
		except:
			print("Erro atualização de BD >>"+updcmd)
			input("	")
		db.commit()

		selcmd = "SELECT * FROM maq WHERE hospedeiro='%s'"%hostid
		db.cursor.execute(selcmd)
		vms = db.cursor.fetchall()

		for vm in vms:
			if vm["nome"] not in ret["all"]:
				input("\t*** VM NOVA encontrada: %s %s"%(vm["nome"],vm["id"]))
				# sql = "UPDATE maq SET estado='%s' WHERE id=%s"%(vm["estado"],vm["id"])
				sql = """INSERT INTO maq (nome, estado, tipo, hospedeiro) VALUES ('%s','%s','%s','%s')
					"""%(vm["nome"],vm["estado"],vm["tipo"],hostid)
				db.cursor.execute(selcmd)
				db.commit()

			if (vm["estado"]=='0' and vm["nome"] not in ret["off"] ) or \
				(vm["estado"]=='1' and vm["nome"] not in ret["on"] ) or \
				(vm["estado"]=='-1' and vm["nome"] not in ret["other"] ):
				input("\t*** Estado alterado VM:  %s %s ( %s )"%(vm["nome"],vm["id"],vm["estado"]))

				sql = "UPDATE maq SET estado='%s' WHERE id=%s"%(vm["estado"],vm["id"])
				db.cursor.execute(selcmd)
				db.commit()


			print("VM "+vm["nome"] + " Ok")


def ipmiInfo(ip,altsec=rootpw):
	print("\tIPMI "+ip)
	# if hostline["altsec"]:
	executa = ['ipmitool','-c', '-I','lanplus','-H', ip, '-U', 'admin', '-P', altsec,'power','status']
	# else:
		# executa = ['ipmitool','-c', '-I','lanplus','-H', ip, '-U', 'admin', '-P', rootpw,'power','status']

	output = subprocess.run(executa, capture_output=True, text=True	)

		# o = {"hostid":hostid,"ip":ip}
	if output.returncode==1:
		return "-1"
	else:
		mensagem = str(output.stdout).strip()
		# o["msg"]= mensagem
		ultima = mensagem.split()[-1]
		if str(ultima)=='on':
			return "1"
		else:
			return "0"


def hostinfo(ip, hostid):
	client = SSHClient()
	client.load_system_host_keys()
	client.load_host_keys("/home/paiva/.ssh/known_hosts")
	try:
		client.connect(ip,username='root',password=rootpw)
	except Exception as ex:
		template = "An exception of type {0} occurred. Arguments:\n{1!r}"
		m = template.format(type(ex).__name__, ex.args)
		return {'STATUS':'ERROR', 'MSG':m}


	ret = {'so':'','kernel':'','STATUS':'OK'}
	client = SSHClient()
	client.load_system_host_keys()
	client.load_host_keys("/home/paiva/.ssh/known_hosts")
	client.connect(ip,username='root',password=rootpw)
	ret['MESSAGE']=""
	stdin, stdout, stderr = client.exec_command("cat /etc/system-release")
	try:
		ret['so'] = stdout.read().decode("utf-8").strip()
	except:
		ret['MESSAGE']+="SO: "+ stderr.read().decode("utf-8")

	stdin, stdout, stderr = client.exec_command("uname -a")
	try:
		ret['kernel'] = stdout.read().decode("utf-8").split(' ')[2]
	except:
		ret['MESSAGE']+="Kernel " + stderr.read().decode("utf-8")

	stdin, stdout, stderr = client.exec_command("grep 'model name' /proc/cpuinfo")
	try:
		li = stdout.readlines()

		ret["n"] = len(li)
		ret['cpu'] = li[0].split('\t: ')[1].strip()
	except:
		ret['MESSAGE']+="CPU " + str( stderr.read() )

	stdin, stdout, stderr = client.exec_command("free | grep Mem:")
	try:
		li = stdout.readline()
		ret["mem"] = " ".join(li.split()).split()[1]
	except:
		ret['MESSAGE']+="CPU " + str( stderr.read() )

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
	# return JSONResponse(content=jsonable_encoder({"on":on,"off":off, "all":all, "other":other, "STATUS":"OK", "MSG":err}))

	ret["on"]=on
	ret["off"]=off
	ret["all"]=all
	ret["other"]=other

	## Coleta MAC das vms
	db = DB()
	updcmd = "UPDATE coletamac SET atualizado=1"
	db.cursor.execute(updcmd)
	db.commit()

	for vm in all:
			stdin, stdout, stderr = client.exec_command('virsh domiflist %s'%(vm))
			linhas = stdout.readlines()
			for l in linhas[2:]:
				p = " ".join(l.split()).split()
				if len(p)<5: continue
				inscmd = """INSERT INTO coletamac (maq,nomevm,mac,interface,tipo,fonte,modelo)
						VALUES (%d,'%s','%s','%s','%s','%s','%s')"""%(hostid,vm,p[4],p[0],p[1],p[2],p[3])
				db.cursor.execute(inscmd)
				db.commit()

	return ret
	# {"on":on,"off":off, "all":all, "other":other, "STATUS":"OK", "MSG":err}

allHosts()
