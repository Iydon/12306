PORT = 8080

run:
	python3 app.py

open:
	sudo iptables -I INPUT -p tcp --dport $(PORT) -j ACCEPT
	sudo iptables -I OUTPUT -p tcp --sport $(PORT) -j ACCEPT

close:
	sudo iptables -I INPUT -p tcp --dport $(PORT) -j DROP
	sudo iptables -I OUTPUT -p tcp --sport $(PORT) -j DROP
