Implementação de Hosts via FastAPI

Como fiz para colocar no ar:

  502  git clone https://github.com/pbandierapaiva/hosts
  503  cd hosts/
  516  virtualenv hostapi
  520  source hostapi/bin/activate
  522  git pull
  527  cd hostapi/
  528  pip  install -r requirements.txt

Se já tiver o ambiente, basta

	source hostapi/bin/activate
	cd hostapi
	uvicorn hostapi:app --reload
