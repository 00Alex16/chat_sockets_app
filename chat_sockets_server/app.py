from Client import Client
import socket

server = socket.socket()
server.bind(("localhost", 8001))
server.listen(5)
print ("####### Servidor para el chat iniciado #######")

while True:
  cli, addr = server.accept()
  cliThread = Client(addr, cli)
  cliThread.start()
  Client.clients.append(cliThread)