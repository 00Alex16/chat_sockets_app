from Command import Command
from Database import Database
import threading, json

class Client(threading.Thread):
  clients = []

  def __init__(self, addressClient, socketClient):
    super(Client, self).__init__()
    self.socketClient = socketClient
    self.addressClient = addressClient
    self.rooms = ['default']
    self.room = 'default'
    self.username = ''
    self.port = ''

  # Se elimina el cliente de la lista estática clients y se cierra la conexión con su socket
  @staticmethod
  def closeSocket(username):
    for client in Client.clients:
      if client.username == username:
        print(f"Sesión terminada de '{client.username}' con dirección: {client.addressClient}")
        Client.clients.remove(client)
        client.socketClient.close()
  
  # Se envía un mensaje de un cliente hacia los demás
  @staticmethod
  def sendMsgUsers(username, msg, room):
    for client in Client.clients:
      if client.getRoom() == room and client.username != username:
        data = {"action": "sendMsg",
                "username": username,
                "message": msg}
        client.socketClient.send(json.dumps(data).encode('utf8'))

  # Se pasa a los clientes que están en determinada sala a la sala por defecto y se les notifica
  @staticmethod  
  def changeClientsRoom(username, room):
    msg = f'He eliminado la sala "{room}" en la que te encontrabas. Así que te han movido a la sala por defecto.'
    for client in Client.clients:
      if client.getRoom() == room and client.username != username:
        data = {"action": "changeRoom",
                "username": username,
                "message": msg}
        client.setRoom('default')
        client.socketClient.send(json.dumps(data).encode('utf8'))

  # Se retornan todas las salas activas en el servidor
  @staticmethod
  def getRooms():
    rooms = {"default"}
    for client in Client.clients:
      for room in client.rooms:
        rooms.add(room)
    return rooms

  # Se retorna un dict con la cantidad de clientes en cada sala
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

  # Se retorna una lista con todos los usernames de los clientes activos en el servidor
  @staticmethod
  def getClientUsernames():
    clientUsernames = []
    for client in Client.clients:
      clientUsernames.append(client.username)
    return clientUsernames

  # Se envía un mensaje desde un cliente hacia otro en específico
  @staticmethod
  def sendMsgToClient(usernameOrigin, usernameDestination, msg):
    for client in Client.clients:
      if client.username == usernameDestination:
        data = {"action": "sendMsg",
                "username": usernameOrigin,
                "message": '<span style="color:#3b0343"><u>Susurro</u>:</span> ' + msg}
        client.socketClient.send(json.dumps(data).encode('utf8'))
        return

  def getRoom(self):
    return self.room
  
  def setRoom(self, room):
    self.room = room

  # Se cambia a un cliente a una sala en específico
  def changeRoom(self, argument):
    result = {}
    if argument not in self.getRooms():
      result = {"action":"commandResult", "message": f"La sala '{argument}' no existe.", "room": self.getRoom()}
      return result
    if argument == self.getRoom():
      result = {"action":"commandResult", "message": f"Ya se encuentra en la sala {argument}.", "room": self.getRoom()}
      return result
    '''if argument in self.rooms:
      # Si la sala exite se hace el cambio
      self.setRoom(argument)
    else:
      # En caso de que la sala no sea del mismo cliente
      self.setRoom(argument)'''
    self.setRoom(argument)
    result = {"action":"commandResult", "message": f"Ha cambiado a la sala '{argument}'.", "room": self.getRoom()}
    return result

  # Método encargado de ejecutar los comandos
  # Los comandos disponibles están en el archivo del enunciado del proyecto
  # También se pueden ver con el comando #help
  def executeCommand(self, command):
    # El comando de exit está implementado en un botón
    commandUtils = Command()
    keyword = commandUtils.getKeyword(command)
    argument = commandUtils.getArgument(command)

    if commandUtils.verifyCommand(command):
      if keyword == 'cR':
        self.rooms.append(argument)
        self.setRoom(argument)
        result = {"action":"commandResult", "message": f"Se creó la sala '{argument}' correctamente.", "room": self.getRoom()}
        return result
      
      if keyword == 'gR':
        return self.changeRoom(argument)
      
      if keyword == 'eR':
        return self.changeRoom('default')
      
      if keyword == 'lR': # Este comando se puede implementar como un botón que levante un modal
        clientsInRooms = self.numberClientsInRooms(self.getRooms())
        listMsg = '''<table border = "1">
                      <tr>
                        <th style="text-align:center">Nombre de la sala</th>
                        <th style="text-align:center">Cantidad de usuarios</th>
                      </tr>'''
        for room, nClients in clientsInRooms.items():
          listMsg += f'''<tr>
                          <td style="text-align:center">{room}</td>
                          <td style="text-align:center">{nClients}</td>
                         </tr>'''
        listMsg += '</table>'
        result = {"action":"commandResult", "data": clientsInRooms,
                  "message": listMsg,
                  "room": self.getRoom()}
        return result

      if keyword == 'dR':
        if argument == 'default' or argument not in self.rooms:
          result = {"action":"commandResult", "message": f"No puedes borrar la sala '{argument}'.", "room": self.getRoom()}
          return result
        else:
          self.rooms.remove(argument)
          # Los clientes que estaban en la sala que se eliminó se mueven a la sala por defecto
          self.changeClientsRoom(self.username, argument)
          if self.getRoom() == argument:
            self.setRoom('default')
            result = {"action":"commandResult", "message": f"Se ha eliminado la sala {argument} y te hemos movido a la sala por defecto.", "room": "default"}
          else:
            result = {"action":"commandResult", "message": f"Se ha eliminado la sala {argument}.", "room": self.getRoom()}
          return result
      
      if command == '#show users':
        clientUsernames = self.getClientUsernames()
        listUsers = '<p>Estos son los usuarios conectados en este momento:</p>'
        for clientUsername in clientUsernames:
          listUsers += f'<p>- {clientUsername}.</p>'
        result = {"action":"commandResult", "message": listUsers, "room": self.getRoom()}
        return result
      
      if keyword == '\\private':
        msg = commandUtils.getMsgToSend(command)
        if argument not in self.getClientUsernames():
          return {"action":"commandResult", "message": f"El usuario '{argument}' no se encuentra conectado.", "room": self.getRoom()}
        if argument == self.username:
          return {"action":"commandResult", "message": "Parece que quieres hablar contigo mismo... Qué tal si pruebas con alguien más.", "room": self.getRoom()}
        else:
          self.sendMsgToClient(self.username, argument, msg)
          message = '<span style="color:#3b0343"><u>Susurraste a ' + argument + '</u>:</span> ' + msg
          return {"action":"commandResult", "message": message, "room": self.getRoom()}
      
      if keyword == 'help':
        commands = commandUtils.commandsDescription()
        listCommands = '<p>Esta es la lista de comandos disponibles:</p><br>'
        for command in commands:
          listCommands += f'<p>- {command}</p>'
        result = {"action":"commandResult", "message": listCommands, "room": self.getRoom()}
        return result

    else:
      return {"action":"commandResult", "message": f"El comando '{command}' no es válido.", "room": self.getRoom()}

  # Se ejecuta el sql para registrar un cliente en la BD
  def register(self, data):
    connection = Database()
    sql = f"""INSERT INTO user 
    (name, lastname, username, password, age, gender) 
    VALUES ("{data['name']}", "{data['lastname']}", "{data['username']}", 
            "{data['password']}", "{data['age']}", "{data['gender']}");"""
    connection.runCreateQuery(sql)
  
  # Se ejecuta el sql para loguear un cliente en la aplicación
  def login(self, data):
    connection = Database()
    sql = f"SELECT password FROM user WHERE username='{data['username']}';"
    password = connection.runVerifyQuery(sql)
    if password == data["password"]:
      return True
    return False
  
  # Se ejecuta sql para obtener el género de un determinado cliente
  def getClientGender(self, username):
    connection = Database()
    sql = f"SELECT gender FROM user WHERE username='{username}';"
    result = connection.runVerifyQuery(sql)
    return result

  # Se ejecuta sql para comprobar que un cliente existe en la BD
  def userExists(self, user):
    connection = Database()
    sql = f"SELECT IF(EXISTS(SELECT username from user where username='{user}'), true, false);"
    result = connection.runVerifyQuery(sql)
    return result
      
  def formatData(self, data):
    return json.dumps(data).encode('utf8')

  # Método principal para ejecutar un hilo por cada cliente en el servidor
  def run(self):
    print(f"Nueva conexión del cliente: {self.addressClient, self.addressClient[0], self.addressClient[1]}")
    while Client.clients:
      try:
        request = json.loads(self.socketClient.recv(1024).decode('utf8'))

        if (request["action"] == 'register'):
          if self.userExists(request["username"]):
            response = {"message": f"El usuario '{request['username']}' ya se encuentra registrado!", "success": False}
            self.socketClient.send(self.formatData(response))
            return
          try:
            self.register(request)
          except Exception as e:
            response = {"message": "Ha ocurrido un error al tratar de crear al usuario", "success": False}
            self.socketClient.send(self.formatData(response))
            return
          response = {"message": "Usuario creado con éxito", "success": True}
          self.socketClient.send(self.formatData(response))

        elif (request["action"] == 'login'):
          if self.userExists(request["username"]):
            if self.login(request):
              # Se almacena nombre de usuario y port en el objeto cliente
              self.username = request["username"]
              self.port = request["port"]
              gender = self.getClientGender(request["username"])
              response = {"message": "Usuario logueado correctamente", "gender": gender, "success": True}
              self.socketClient.send(self.formatData(response))
            else:
              response = {"message": "La contraseña no coincide con el usuario", "success": False}
              self.socketClient.send(self.formatData(response))
          else:
            response = {"message": f"El usuario '{request['username']}' no existe", "success": False}
            self.socketClient.send(self.formatData(response))

        elif (request["action"] == 'sendMsg'):
          if (request["msg"][0] == '#'):
            response = self.executeCommand(request["msg"])
            self.socketClient.send(self.formatData(response))
          else:
            self.sendMsgUsers(request["username"], request["msg"], self.getRoom())
            #response = {"action": "msgResult", "message": "Mensaje enviado", "room": self.getRoom()}
            #self.socketClient.send(self.formatData(response))
        
        elif (request["action"] == 'close'):
          response = {"action": "close", "message": "Sesión terminada"}
          self.socketClient.send(self.formatData(response))
          self.closeSocket(self.username)
          break
      except Exception as e:
        print(f"Ha ocurrido un error en la ejecución del hilo del cliente: {self.addressClient}.")
        print(e)
        break