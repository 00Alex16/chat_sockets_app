from Client import Client
import socket

server = socket.socket()
# En caso de ejecutar el servidor localmente usar 'localhost', 8001
server.bind(("", 3389))
server.listen(5)
print ("####### Servidor para el chat iniciado #######")

while True:
  try:
    cli, addr = server.accept()
    cliThread = Client(addr, cli)
    cliThread.start()
    Client.clients.append(cliThread)
  except Exception as e:
    print(f"Ha ocurrido un error al tratar de iniciar un nuevo hilo: {e}")
    break