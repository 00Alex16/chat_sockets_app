import json

def sendData(data, sClient):
    sClient.send(data.encode('utf8'))
    response = json.loads(sClient.recv(1024).decode('utf8'))

    return response