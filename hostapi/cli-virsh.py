##
## Utiliza lib virsh para acessar dados de guests
##

import libvirt
import sys
# import xml
import xml.etree.ElementTree as ET

auth = [[libvirt.VIR_CRED_AUTHNAME, libvirt.VIR_CRED_PASSPHRASE],'root','3e4rfgt5']


try:
	conn = libvirt.open('qemu+ssh://root@10.90.0.213/system') #,auth,0)
except libvirt.libvirtError as e:
	print(repr(e),file=sys.stderr)
	exit(1)

for d in conn.listAllDomains():  #libvirt.VIR_CONNECT_LIST_DOMAINS_ACTIVE):
	print(d.name(), d.isActive(), d.isPersistent())
	
	raiz= ET.fromstring(d.XMLDesc())
	# print(d.XMLDesc())
	# for x in raiz.findall('mac'):
	# 	print("XXXXX",x.attribute())
		
	for el in raiz:
		if el.tag=='devices':
			for el2 in el:
				if el2.tag=='interface':
					for el3 in el2:
						if el3.tag=='mac':
							print("\t",el3.attrib['address'])
	
		
		
		