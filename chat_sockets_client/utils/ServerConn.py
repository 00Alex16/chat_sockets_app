import threading, json, requests

url = 'http://127.0.0.1:5001/chat'

class ServerConn(threading.Thread):
  def __init__(self, socket, username):
    super(ServerConn, self).__init__()
    self.socket = socket
    self.username = username

  def close(self):
    print("Termina la ejecución del hilo que escucha las respuestas del servidor en el chat")
    self.socket.close()
  
  def run(self):
    print("Comienza la ejecución del hilo que escucha las respuestas del servidor en el chat")
    while True:
      try:
        data = self.socket.recv(1024).decode('utf8')
        if data:
          response = json.loads(data)
          if response["action"] == "close":
            self.close()
            break
          requests.post(url, json=response)
      except Exception as e:
        print(e)
        break