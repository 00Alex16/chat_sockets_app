class Command():
  def __init__(self):
    self.commandsArgument = ['cR', 'gR', 'dR']
    self.commandsNoArgument = ['eR', 'lR']
    self.otherCommands = ['\private', 'show users']
  
  def getKeyword(self, command):
    keyword = ''
    for i in command:
      if (i != ' '):
        keyword += i
      else:
        break
    return keyword.replace('#', '')
  
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

  def getArgument(self, command):
    argument = ''
    flag = False
    for i in command:
      if (i == ' '):
        flag = True
      if flag:
        argument += i
    return self.getMsg(argument[1:])[0]
  
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
    keyword = self.getKeyword(command)
    if (keyword in self.commandsArgument):
      if len(self.getArgument(command)) > 0:
        return True
    
    elif (keyword in self.commandsNoArgument):
      if len(self.getArgument(command)) == 0:
        return True

    elif (command == 'show users'):
      return True

    elif (keyword == '\private'):
      if len(self.getArgument(command)) > 0 and len(self.getMsg) > 0:
        return True
    
    else:
      return False