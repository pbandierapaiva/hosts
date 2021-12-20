from django.db import models

class Host(models.Model):
    nome = models.CharField(primary_key=True, max_length=100)
    net_mgmt = models.CharField(max_length=15, default="", blank=True)
    net_164 = models.CharField(max_length=15, default="", blank=True)
    net_162 = models.CharField(max_length=15, default="", blank=True)
    net_dmz = models.CharField(max_length=15, default="", blank=True)
    net_1080 = models.CharField(max_length=15, default="", blank=True)
    net_1090 = models.CharField(max_length=15, default="", blank=True)
    modelo = models.CharField(max_length=100, default="", blank=True)
    cpu  = models.CharField(max_length=100, default="", blank=True)
    ncpu = models.IntegerField(null=True, blank=True)
    mem = models.IntegerField(null=True, blank=True)
#    data = models.DateTimeField('data', default='2021-01-01')
    
    def __str__(self):
    	return self.nome
    
class VM(models.Model):
	host = models.ForeignKey(Host, on_delete=models.CASCADE)
	nome = models.CharField(max_length=100, blank=True)
	ncpu = models.IntegerField(null=True, blank=True)
	mem = models.IntegerField(null=True, blank=True)
#	data = models.DateTimeField('data', default='2021-01-01')
	def __str__(self):
		return self.nome



