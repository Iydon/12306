HOST = 0.0.0.0
PORT = 8080

run:
	flask run --host $(HOST) --port $(PORT)

open:
	sudo iptables -I INPUT -p tcp --dport $(PORT) -j ACCEPT
	sudo iptables -I OUTPUT -p tcp --sport $(PORT) -j ACCEPT

close:
	sudo iptables -I INPUT -p tcp --dport $(PORT) -j DROP
	sudo iptables -I OUTPUT -p tcp --sport $(PORT) -j DROP

docker_deploy:
	docker build -t cs307-project-2 .

docker_run:
	docker run -p $(PORT):$(PORT) cs307-project-2
