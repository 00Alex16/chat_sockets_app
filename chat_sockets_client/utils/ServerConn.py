# Esta clase no se está usando porque estaba generando problemas
import threading, json, requests

url = 'http://127.0.0.1:5001/chat'

class ServerConn(threading.Thread):
  def __init__(self, socket, username):
    super(ServerConn, self).__init__()
    self.socket = socket
    self.username = username

  def close(self):
    self.socket.close()
  
  def run(self):
    print("Comienzo la ejecución del hilo")
    while True:
      try:
        data = self.socket.recv(1024).decode('utf8')
        if data:
          response = json.loads(data)
          # Cuando se recibe un mensaje de otro cliente
          if (response["action"] == "sendMsg"):
            requests.post(url, json=response)
      except Exception as e:
        print(e)