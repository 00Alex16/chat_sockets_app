from dataclasses import dataclass
from Database import Database
import threading, json

class Client(threading.Thread):
  clients = []

  def __init__(self, addressClient, socketClient):
    super(Client, self).__init__()
    self.socketClient = socketClient
    self.addressClient = addressClient

  @staticmethod
  def closeSocket(addressClient):
    for client in Client.clients:
      if client.self.addressClient == addressClient:
        Client.clients.remove(client)
        client.socketClient.close()

  def register(self, data):
    connection = Database()
    sql = f"""INSERT INTO user 
    (name, lastname, username, password, age, gender) 
    VALUES ("{data['name']}", "{data['lastname']}", "{data['username']}", 
            "{data['password']}", "{data['age']}", "{data['gender']}");"""
    connection.runCreateQuery(sql)
  
  def login(self, data):
    connection = Database()
    sql = f"SELECT password FROM user WHERE username='{data['username']}';"
    password = connection.runVerifyQuery(sql)
    if password == data["password"]:
      return True
    return False

  def userExists(self, user):
    connection = Database()
    sql = f"SELECT IF(EXISTS(SELECT username from user where username='{user}'), true, false);"
    result = connection.runVerifyQuery(sql)
    return result


  def run(self):
    request = json.loads(self.socketClient.recv(1024).decode('utf8'))
    if (request["action"] == 'register'):
      try:
        self.register(request)
      except Exception as e:
        response = {"message": "Ha ocurrido un error al tratar de crear al usuario"}
        self.socketClient.send(json.dumps(response).encode('utf8'))
        self.socketClient.close()
        return
      response = {"message": "Usuario creado con éxito"}
      self.socketClient.send(json.dumps(response).encode('utf8'))
    elif (request["action"] == 'login'):
      if self.userExists(request["username"]):
        if self.login(request):
          response = {"message": "Usuario logueado correctamente"}
          self.socketClient.send(json.dumps(response).encode('utf8'))
          self.socketClient.close()
        else:
          response = {"message": "La contraseña no coincide con el usuario"}
          self.socketClient.send(json.dumps(response).encode('utf8'))
          self.socketClient.close()
      else:
        response = {"message": "El usuario no existe"}
        self.socketClient.send(json.dumps(response).encode('utf8'))
        self.socketClient.close()
    self.socketClient.close()