from django.urls import path

from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('host/', views.hosts, name='hosts-d'),
	path('host/<str:host_id>', views.hosts, name='detail'),



]

