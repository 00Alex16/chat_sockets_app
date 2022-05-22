from Command import Command
from Database import Database
import threading, json, requests

class Client(threading.Thread):
  clients = []

  def __init__(self, addressClient, socketClient):
    super(Client, self).__init__()
    self.socketClient = socketClient
    self.addressClient = addressClient
    self.rooms = ['default']
    self.ownRooms = ['default']
    # Hay que cambiar la lógica de self.room
    self.room = 'default'
    self.username = ''
    self.port = ''

  @staticmethod
  def closeSocket(username):
    for client in Client.clients:
      if client.username == username:
        print("coincide")
        Client.clients.remove(client)
        client.socketClient.close()
  
  @staticmethod
  def sendMsgUsers(username, msg, room):
    for client in Client.clients:
      if client.getRoom() == room and client.username != username:
        data = {"action": "sendMsg",
                "username": username,
                "msg": msg}
        requests.post('http://127.0.0.1:' + client.port + '/chat', json=data)
        #client.socketClient.send(json.dumps(data).encode('utf8'))

  @staticmethod
  def getRooms():
    rooms = {"default"}
    for client in Client.clients:
      for room in client.rooms:
        rooms.add(room)
    return rooms

  @staticmethod
  def numberClientsInRooms(rooms):
    nClientsInRooms = {}
    for room in rooms:
      counter = 0
      nClientsInRooms[room] = counter
      for client in Client.clients:
        if client.getRoom() == room:
          counter += 1
          nClientsInRooms[room] = counter
    return nClientsInRooms

  @staticmethod
  def getClientUsernames():
    clientUsernames = []
    for client in Client.clients:
      clientUsernames.append(client.username)
    return clientUsernames

  @staticmethod
  def sendMsgToClient(usernameOrigin, usernameDestination, msg):
    for client in Client.clients:
      if client.username == usernameDestination:
        data = {"action": "privateMsg",
                "username": usernameOrigin,
                "msg": msg}
        client.socketClient.send(json.dumps(data).encode('utf8'))

  def getRoom(self):
    return self.rooms[len(self.rooms)-1]

  def changeRoom(self, argument):
    result = {}
    if argument not in self.getRooms():
      result = {"action":"commandResult", "message": "La sala no existe", "room": self.getRoom()}
      return result
    if argument == self.getRoom():
      result = {"action":"commandResult", "message": "Ya se encuentra en la sala", "room": self.getRoom()}
      return result
    if argument in self.rooms:
      # Para colocar a la sala en la última posición
      self.rooms.remove(argument)
      self.rooms.append(argument)
    else:
      # En caso de que la sala no sea del mismo cliente
      self.room = argument    # PUEDE LLEGAR A DAR PROBLEMAS ESTA LÓGICA
    result = {"action":"commandResult", "message": "Ha cambiado de sala", "room": self.getRoom()}
    print("result")
    return result

  def executeCommand(self, command):
    # El comando de exit está implementado en un botón
    print("Entre al command antes con request: ", command)
    commandUtils = Command()
    keyword = commandUtils.getKeyword(command)
    argument = commandUtils.getArgument(command)
    print("Entre al command despues con request: ", command)
    print(keyword, argument)

    if commandUtils.verifyCommand(command):
      if keyword == 'cR':
        print("Entre al command server con request: ", command)
        self.rooms.append(argument)
        result = {"action":"commandResult", "message": "Se creó la sala correctamente.", "room": self.getRoom()}
        return result
      
      if keyword == 'gR':
        return self.changeRoom(argument)
      
      if keyword == 'eR':
        print("Entre al eR")
        return self.changeRoom('default')
      
      if keyword == 'lR': # Este comando se puede implementar como un botón que levante un modal
        clientsInRooms = self.numberClientsInRooms(self.getRooms())
        result = {"action":"commandResult", "data": clientsInRooms,
                  "message": "Lista de salas y cantidad de participantes en cada una",
                  "room": self.getRoom()}
        return result

      if keyword == 'dR':
        if argument == 'default' or argument not in self.rooms:
          result = {"action":"commandResult", "message": "No puedes borrar esta sala", "room": self.getRoom()}
          return result
        else:
          self.rooms.remove(argument)
          # Cambiar a todos los demás clientes que esten en esa sala
      
      if keyword == 'show users':
        result = {"message": "Lista de usuarios conectados", "users": self.getClientUsernames()}
        return result
      
      if keyword == '\\private':
        msg = commandUtils.getMsgToSend()
        self.sendMsgToClient(self.username, argument, msg)
        return {"message": "Se envió el mensaje"}

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
      
  def formatData(self, data):
    return json.dumps(data).encode('utf8')

  def run(self):
    print(f"Nueva conexión del cliente: {self.addressClient, self.socketClient}")
    while Client.clients:
      try:
        request = json.loads(self.socketClient.recv(1024).decode('utf8'))

        if (request["action"] == 'register'):
          try:
            self.register(request)
          except Exception as e:
            response = {"message": "Ha ocurrido un error al tratar de crear al usuario"}
            self.socketClient.send(self.formatData(response))
            self.socketClient.close()
            return
          response = {"message": "Usuario creado con éxito"}
          self.socketClient.send(self.formatData(response))

        elif (request["action"] == 'login'):
          if self.userExists(request["username"]):
            if self.login(request):
              # Se almacena nombre de usuario y port en el objeto cliente
              self.username = request["username"]
              self.port = request["port"]
              response = {"message": "Usuario logueado correctamente", "success": True}
              self.socketClient.send(self.formatData(response))
            else:
              response = {"message": "La contraseña no coincide con el usuario", "success": False}
              self.socketClient.send(self.formatData(response))
          else:
            response = {"message": "El usuario no existe", "success": False}
            self.socketClient.send(self.formatData(response))

        elif (request["action"] == 'sendMsg'):
          if (request["msg"][0] == '#'):
            print("Entre al server con request: ", request)
            response = self.executeCommand(request["msg"])
            self.socketClient.send(self.formatData(response))
          else:
            self.sendMsgUsers(request["username"], request["msg"], self.getRoom())
            response = {"action": "msgResult", "message": "Mensaje enviado", "room": self.getRoom()}
            self.socketClient.send(self.formatData(response))
        
        elif (request["action"] == 'close'):
          response = {"message": "Sesión terminada"}
          self.socketClient.send(self.formatData(response))
          self.closeSocket(self.username)
      except Exception as e:
        print(e)