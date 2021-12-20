
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
    	estadoHost = document.createElement("span")
    	estadoHost.innerHTML = "&nbsp;"
    	
    	ipmi = document.createElement("a")
    	ipmi.className = "w3-button w3-tiny w3-border w3-round-large w3-right"
    	ipmi.href = "http://"+i.redes.ipmi
    	ipmi.target="_blank"
    	ipmi.innerHTML = i.redes.ipmi


    	estadoHost.className="w3-badge w3-right w3-margin-right "
      	if( i.estado==0 ) estadoHost.className+="w3-grey"
    	else {
    		if(i.estado==1) estadoHost.className+="w3-green"
    		else estadoHost.className+="w3-yellow"
    		}
    	item.innerHTML = i.nome    		
	item.href = '/hosts/'+i.id
	item.target='infoarea'
    	item.appendChild(estadoHost)    		
    	item.appendChild(ipmi)

    	document.getElementById("listahost").appendChild(item)
    }
  }

