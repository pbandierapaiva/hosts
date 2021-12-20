
function carregaHosts() {
  const xhttp = new XMLHttpRequest();
  xhttp.onload = function() {

    li = document.createElement("ul")
    li.className="w3-ul w3-hoverable w3-border"
    
    for (i of JSON.parse(this.responseText)) {
    	item = document.createElement("li")
    	//celula = document.createElement("div")
    	estadoHost = document.createElement("span")
    	estadoHost.innerHTML = "&nbsp;"
    	nomehost = document.createElement("a")
    	nomehost.href = "http://"+i.ip
    	nomehost.innerHTML = i.nome
      	if( i.estado==0 ) {
    		estadoHost.className="w3-badge w3-right w3-margin-right w3-grey"
    		}
    	else {
    		if(i.estado==1) {
    			estadoHost.className="w3-badge w3-right w3-margin-right w3-green"
    			}
    		else {
    			estadoHost.className="w3-badge w3-right w3-margin-right w3-yellow"
    			}
    		}
    	item.appendChild(estadoHost)
    	item.appendChild(nomehost)         //document.createTextNode(i.nome))
    	//item.innerHTML =  i.nome 
    	li.appendChild ( item )
    	document.getElementById("listahost").appendChild(li)
    }
  }
  xhttp.open("GET", "/hosts");	
  xhttp.send();
}
