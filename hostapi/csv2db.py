## Import CSV to DB

import mariadb

from conexao import conexao

# Estabelece conexão
db= mariadb.connect(**conexao)

cursor= db.cursor()

def cleanAll():
	cursor.execute("delete from netdev")
	cursor.execute("delete from maq")
	cursor.execute("delete from rede")

def defineNets():
	cursor.execute("delete from rede")
	for rec in [
				('ipmi','10.90.8.0/24','10.90.8.1',998),
				('160','172.22.160.0/22','172.22.160.1',164),
				('164','172.22.164.0/22','172.22.164.1',111),
				('dmz','200.144.92.128/26','200.144.93.129',4),
				('cloud','10.100.0.0/24','10.100.0.1',1000),
				('core','10.80.0.0/24','10.80.0.1',800),
				('fog','10.99.9.0/24','10.99.9.1',999),
				('under','10.90.0.0/24','10.90.0.1',900)
		]:
		cmd = "insert into rede (nome,cidr,gateway,vlan) values ('%s','%s','%s',%d)"
		print(cmd%rec)
		cursor.execute(cmd%rec)

	db.commit()


def csv(fn='IPMI-Equips.csv'):
	cursor.execute("delete from maq")
	if fn!= 'IPMI-Equips.csv':
		fn = input("CSV: ")
	inf = open(fn)
	while True:
		li = inf.readline()
		if  not li: break
		p = li.split(',')
		if p[0]=='': continue
		
		cmd = "insert into maq (nome, tipo, estado) values('%s','%s','%d')"
		if p[8]=='ON':
			estado=1
		else:		
			estado=0

		cursor.execute(cmd%(p[6],p[1],estado )) 
		maq = cursor.lastrowid 

		if p[2]!='' and '*' not in p[2]:
			cmd = "insert into netdev (ip, rede, maq) values('%s','%s',%d)"
			cursor.execute(cmd%(p[2], 'ipmi', maq))		
		if p[10]!='' and '*' not in p[10]:
			cmd = "insert into netdev (ip, rede, maq) values('%s','%s',%d)"
			cursor.execute(cmd%(p[10], 'dmz', maq))
		if p[11]!='' and '*' not in p[11]:
			cmd = "insert into netdev (ip, rede, maq) values('%s','%s',%d)"
			cursor.execute(cmd%(p[11], '164', maq))
		if p[12]!='' and '*' not in p[12]:
			cmd = "insert into netdev (ip, rede, maq) values('%s','%s',%d)"
			cursor.execute(cmd%(p[12], '160', maq))
		if p[13]!='' and '*' not in p[13]:
			cmd = "insert into netdev (ip, rede, maq) values('%s','%s',%d)"
			cursor.execute(cmd%(p[13], 'core', maq))
		if p[14]!='' and '*' not in p[14]:
			cmd = "insert into netdev (ip, rede, maq) values('%s','%s',%d)"
			cursor.execute(cmd%(p[14], 'under', maq))
		if p[15]!='' and '*' not in p[15]:
			cmd = "insert into netdev (ip, rede, maq) values('%s','%s',%d)"
			cursor.execute(cmd%(p[13], 'core', maq))

			
			
			
		db.commit()

c= input("********* ATENÇÃO *********\nEsta operação zera os BDs\n\nConfirma?")
if c!='sim':
	print("Operação cancelada.")
	exit()
cleanAll()
defineNets()
csv()
