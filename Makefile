HOST = 0.0.0.0
PORT = 8080
PROJECT = cs307-project-2

run:
	export FLASK_APP=code \
		&& flask run --host $(HOST) --port $(PORT)

open:
	sudo iptables -I INPUT -p tcp --dport $(PORT) -j ACCEPT
	sudo iptables -I OUTPUT -p tcp --sport $(PORT) -j ACCEPT

close:
	sudo iptables -I INPUT -p tcp --dport $(PORT) -j DROP
	sudo iptables -I OUTPUT -p tcp --sport $(PORT) -j DROP

docker_deploy:
	docker build -t $(PROJECT) .

docker_run:
	docker run -p $(PORT):$(PORT) $(PROJECT)
