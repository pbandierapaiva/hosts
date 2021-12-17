from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import Host

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")
    

def hosts(request, host_id=None):

	if not host_id:
		listah = Host.objects.all()
		
		template = loader.get_template('hostapp/index.html')
		context = {
			'lista_h': listah,
 			}
		return HttpResponse(template.render(context, request))

		
		
		if len(listah)==0: return HttpResponse("Sem Hosts")
		output = ', '.join([ h.nome for h in listah])
		return HttpResponse("Hosts: "+ output)
	
	return HttpResponse("Host "+str(host_id))
	

def load(request):
	return HttpResponse("Load")
	
