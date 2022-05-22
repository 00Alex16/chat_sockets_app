class Command():
  def __init__(self):
    self.commands = ['#cR', '#gR', '#eR', 'lR', 'dR', 'show users', '\private']
  
  def getKeyword(self, command):
    keyword = ''
    for i in command:
      if (i != ' '):
        keyword += i
      else:
        break
    return keyword
  
  def getArgument(self, command):
    argument = ''
    flag = False
    for i in command:
      if (i == ' '):
        flag = True
      if flag:
        argument += i
    return argument.replace(' ', '')
  
  def getMsgToSend(self, command):
    msg = ''
    counter = 0
    for i in command:
      if (i == ' '):
        counter += 1
      if counter >= 2:
        msg += i
    return msg

  def verifyCommand(self, command):
    # Falta hacer más validaciones
    if self.getKeyword(command) in self.commands and len(self.getArgument(command)) > 0:
      return True
    
  def cRCommand(self, argument):
    roomName = argument
    return roomName

  def gRCommand(self, argument):
    roomName = argument
    return roomName

  def eRCommand(self):
    pass

  def lRCommand(self):
    pass

  def dRCommand(self):
    pass

  def exitCommand(self):
    pass

  def showUsersCommand(self):
    pass

  def privateCommand(self):
    pass