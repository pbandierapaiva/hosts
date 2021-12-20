
function carregaHosts() {
  const xhttp = new XMLHttpRequest();
  xhttp.onload = onLoadHosts;
  xhttp.open("GET", "/hosts");	
  xhttp.send();
}

function onLoadHosts(){

//    li = document.createElement("ul")
//    li.className="w3-ul w3-hoverable w3-border"
    li = document.createElement("a")

    
    for (i of JSON.parse(this.responseText)) {
    	item = document.createElement("a")
    	item.className="w3-bar-item w3-button"
    	//celula = document.createElement("div")
    	estadoHost = document.createElement("span")
    	estadoHost.innerHTML = "&nbsp;"
    	//nomehost = document.createElement("a")
    	//nomehost.className = "w3-button w3-black"
    	item.href = "http://"+i.ip
    	item.target="#infoarea"
    	item.innerHTML = i.nome
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
    	//item.appendChild(nomehost)         //document.createTextNode(i.nome))
    	//item.innerHTML =  i.nome 
    	//li.appendChild ( item )
    	document.getElementById("listahost").appendChild(item)
    }
  }

