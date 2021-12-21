
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
   	
   	barraStatus = document.createElement("div")
   	barraStatus.className = "w3-bar"
   	
    	ipmi = document.createElement("a")
    	ipmi.className = "w3-button w3-tiny w3-border w3-round "
    	ipmi.style = "width:30%"
    	ipmi.href = "http://"+i.redes.ipmi
    	ipmi.target="_blank"
    	ipmi.innerHTML = i.redes.ipmi
    	
    	tipo = document.createElement("a")
    	tipo.className = "w3-button w3-tiny w3-border w3-center w3-round "
    	tipo.style = "width:10%"
	switch( i.tipo ){
		case "H":
			tipo.innerHTML = "VM"
			tipo.className += "w3-blue"
			break;
		case "S":
			tipo.innerHTML = "ST"
			tipo.className += "w3-teal"
			break;
		default:
			tipo.innerHTML = "??"
			break;
		}
			
    	estadoHost = document.createElement("span")
    	estadoHost.innerHTML = "&nbsp;"
    	estadoHost.className="w3-button w3-tiny w3-border w3-round "
    	estadoHost.style = "width:3%"
      	if( i.estado==0 ) estadoHost.className+="w3-grey"
    	else {
    		if(i.estado==1) estadoHost.className+="w3-green"
    		else estadoHost.className+="w3-yellow"
    		}
    	nomeHost = document.createElement("span")
    	nomeHost.innerHTML = i.nome  
    	nomeHost.className="w3-button w3-tiny w3-border w3-round "
    	nomeHost.style = "width:40%"

    	barraStatus.appendChild(nomeHost)
    	barraStatus.appendChild(ipmi)
    	barraStatus.appendChild(tipo)
	barraStatus.appendChild(estadoHost)
    	
    	item = document.createElement("a")
    	item.className="w3-bar-item w3-button"		
	item.href = '/hosts/'+i.id
	item.target='infoarea'
    	item.appendChild(barraStatus)

    	document.getElementById("listahost").appendChild(item)
    }
  }

