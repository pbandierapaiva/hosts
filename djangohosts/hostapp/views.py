from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import Host

def index(request):
    return HttpResponse("Index.")
    

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
	else:
		try:
			h = Host.objects.get(nome=host_id)
		except:
			raise Http404("Host não existe.")

	return HttpResponse("Host "+str(host_id))
	

def load(request):
	return HttpResponse("Load")
	
