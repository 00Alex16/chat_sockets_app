from utils.socketClient import sendData
from utils.ServerConn import ServerConn
from flask import Flask, render_template, request, redirect, url_for, flash
import json, socket

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'    # Secret key para poder usar session y flash

# Variables globales
msgHistory = None
username = None
imgUrl = None
room = None

@app.route("/", methods=['POST', 'GET'])
def login():
    global imgUrl, room

    if (request.method == 'POST'):
        data = {"action": "login",
                "username": request.form["username"],
                "password": request.form["password"],
                "port": port}
        response = sendData(json.dumps(data), socketClient)

        if response["success"]:
            # Session permite guardar variables en la sesión de un cliente
            # En vez de session se usaron variables globales
            global username
            if response["gender"] == 'male':
                imgUrl = '../static/images/male-icon.png'
            else:
                imgUrl = '../static/images/female-icon.png'
            room = 'default'
            username = data["username"]

            # Se inicia hilo que va a estar escuchando las respuestas del servidor en el chat
            msgListening = ServerConn(socketClient, data["username"])
            msgListening.start()

            return redirect(url_for('chat'))
        else:
            # flash permite guardar mensajes de retroalimentación en el siguiente request
            flash(response["message"], "alertError")
            return redirect(url_for('login'))

    return render_template("login.html")

@app.route("/register", methods=['POST', 'GET'])
def register():
    if (request.method == 'POST'):
        data = {"action": "register",
                "name": request.form["name"],
                "lastname": request.form["lastname"],
                "username": request.form["username"],
                "password": request.form["password"],
                "age": request.form["age"],
                "gender": request.form["gender"]}
        response = sendData(json.dumps(data), socketClient)
        if response["success"]:
            flash(response["message"], "alertSuccess")
        else:
            flash(response["message"], "alertError")

    return render_template("register.html")

@app.route("/chat", methods=['POST', 'GET'])
def chat():
    # Variables que se usan en el transcurso del chat
    global msgHistory, imgUrl, room, username
    msg = ''
    msgSentBy = ''

    if (request.method == 'POST'):
        if (request.is_json):
            # Se reciben las requests desde el hilo msgListening
            if request.get_json()["action"] == 'sendMsg':
                msgSentBy = request.get_json()["username"]
                msg = request.get_json()["message"]

            if request.get_json()["action"] == 'changeRoom':
                msgSentBy = request.get_json()["username"]
                msg = request.get_json()["message"]
                room = 'default'

            if request.get_json()["action"] == 'commandResult':
                msgSentBy = 'Sistema'
                msg = request.get_json()["message"]
                room = request.get_json()["room"]
        else:
            # En caso contrario es el request desde el form
            msg = request.form['message']
            data = {"action": "sendMsg",
                    "username": username,
                    "msg": msg,}
            msgSentBy = data["username"]
            if msg:
                socketClient.send(json.dumps(data).encode('utf8'))
                if msg[0] == '#':
                    msg = ''
            
    if not msgHistory:
        msgHistory = []
        msgHistory.append(['Sistema', 'Puedes escribir #help para ver los comandos disponibles'])
    if msg and msgSentBy:
        msgHistory.append([msgSentBy, msg])
    return render_template("room.html", msgList=msgHistory, username=username, 
                            room=room, imgUrl=imgUrl)

@app.route("/closeSession", methods=['POST', 'GET'])
def closeSession():
    global username

    data = {"action": "close"}
    socketClient.send(json.dumps(data).encode('utf8'))

    return render_template("closeSession.html", username=username)

if __name__ == "__main__":
    port = '5001'
    # Socket que se utiliza en el lado del cliente
    socketClient = socket.socket()
    # Información para conectarse al servidor remoto
    socketClient.connect(("34.125.209.94", 3389))

    app.run(debug=False, port=port)