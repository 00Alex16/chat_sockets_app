import socket, json

def sendData(data):
    addr = "localhost"
    port = 8001
    sClient = socket.socket()
    sClient.connect((addr, port))
    sClient.send(data.encode('utf8'))
    response = json.loads(sClient.recv(1024).decode('utf8'))
    sClient.close()

    return response