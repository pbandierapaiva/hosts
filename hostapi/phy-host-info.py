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

	sosim = input("Incluir verificação SO?")
	vmsim = input("Verificar VMs")

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

		if hostline["estado"]==status:
			print("Status OK ", status)
		else:
			print("Status ALTERADO", status)
			updcmd = "UPDATE maq SET estado='%s'	WHERE id='%s'"%(status,hostid)
			print(updcmd)
			try:
				print("Alterando estado "+status)
				status = db.cursor.execute(updcmd)
			except:
				input("Erro inserção BD >>"+updcmd)

			db.commit()

		if status!="1":
			continue
		# continue

		print("SSH Host")

		for ip in li['redes']:
			ret = hostinfo(ip)
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
		#h["maq"])

		#print(updcmd)
		try:
			print("inserindo "+str(ret))
			status = db.cursor.execute(updcmd)
		except:
			print("Erro inserção BD >>"+updcmd)
			input("	")
		db.commit()

		selcmd = "SELECT * FROM maq WHERE hospedeiro='%s'"%hostid
		db.cursor.execute(selcmd)
		vms = db.cursor.fetchall()

		for vm in vms:
			if vm["nome"] not in ret["all"]:
				input("\t*** VM NOVE encontrada: %s %s"%(vm["nome"],vm["id"]))
			if (vm["estado"]=='0' and vm["nome"] not in ret["off"] ) or \
				(vm["estado"]=='1' and vm["nome"] not in ret["on"] ):
				input("\t*** Estado alterado VM:  %s %s ( %s )"%(vm["nome"],vm["id"],vm["estado"]))
			print("VMs Ok")


		print(ret)

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


def hostinfo(ip):
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

	return ret
	# {"on":on,"off":off, "all":all, "other":other, "STATUS":"OK", "MSG":err}

allHosts()
