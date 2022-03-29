from browser import document
from browser import html, ajax, alert, confirm, prompt

from browser.widgets.dialog import InfoDialog, Dialog

from rack import *
from hostinfo import *
from utils import *

import json


# rack = Rack()

cabecalho = html.DIV("DCP-DIS-EPM-Unifesp", id="cabecalho", Class="w3-bar w3-card-2 notranslate")
busca = html.A(Class="w3-bar-item w3-button w3-hover-none w3-left w3-padding-4  w3-right")
busca <= html.I(Class="fa fa-search")
busca.bind("click", buscaNo)
cabecalho<=busca

# main = html.DIV(id="main", Class="w3-container w3-cell")
# main.style={"overflow": "hidden"} #"display": "table-row"}     #, "overflow": "hidden"} #
# infoarea = html.DIV(id="infoarea", Class="w3-container w3-light-grey")
# infoarea.style = {"display": "table-cell"}  #{"margin-left":"220px"}
# infoarea.style = {"flex-grow":"1"}

document <= cabecalho
# main <= rack
# main <= infoarea
# document <= main

document <= Rack()
document <= InfoArea()


# def inicia():
# document["listahost"] <= HostList(


# confirma = Confirma("TESTE", inicia)

# Coloca lista de Hosts na área
	# document["listahost"] <= HostList()
# 	Alerta("SIM")
# else:
# 	Alerta("Não")
