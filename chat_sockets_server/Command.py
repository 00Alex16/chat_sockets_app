class Command():
  def __init__(self):
    self.commandsArgument = ['cR', 'gR', 'dR']
    self.commandsNoArgument = ['eR', 'lR', 'help']
    self.otherCommands = ['\private', 'show users']
  
  # Se retorna la palabra clave del comando
  def getKeyword(self, command):
    keyword = ''
    for i in command:
      if (i != ' '):
        keyword += i
      else:
        break
    return keyword.replace('#', '')
  
  # Para el caso del comando \private se retorna el usuario y mensaje
  def getMsg(self, command):
    argument = ''
    msg = ''
    flag = False
    for i in command:
      if (i == ' '):
        flag = True
      if flag:
        msg += i
      else:
        argument += i
    argument = argument.replace(' ', '')
    msg = msg[1:]
  
    return [argument, msg]

  # Se obtiene el argumento para el comando (puede ser una sala o usuario)
  def getArgument(self, command):
    argument = ''
    flag = False
    for i in command:
      if (i == ' '):
        flag = True
      if flag:
        argument += i
    return self.getMsg(argument[1:])[0]
  
  # Para el caso del comando \private se retorna el mensaje
  def getMsgToSend(self, command):
    msg = ''
    counter = 0
    for i in command:
      if (i == ' '):
        counter += 1
      if counter >= 2:
        msg += i
    return msg

  # Se verifica que el comando sea válido
  def verifyCommand(self, command):
    keyword = self.getKeyword(command)
    if (keyword in self.commandsArgument):
      if len(self.getArgument(command)) > 0:
        return True
    
    elif (keyword in self.commandsNoArgument):
      if len(self.getArgument(command)) == 0:
        return True

    elif (command == '#show users'):
      return True

    elif (keyword == '\private'):
      if len(self.getArgument(command)) > 0 and len(self.getMsg(command)) > 0:
        return True
    
    else:
      return False
    
  def commandsDescription(self):
    commands = ["#cR nombreSala: Crear sala con el nombreSala.",
                "#gR nombreSala: Entrar a la sala nombreSala.",
                "#eR: Salir de la sala en que se encuentra.",
                "#lR: Lista el nombre de todas las salas disponibles y el número de participantes en cada una.",
                "#dR nombreSala: Elimina la sala nombreSala. Solo puedes borrar las salas que creaste.",
                "#show users: Se muestra el listado de usuarios activos.",
                "#\private nombreUsuario mensaje: Envía un mensaje privado a nombreUsuario."]
    return commands