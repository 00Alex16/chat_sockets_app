from utils.socketClient import sendData
from utils.ServerConn import ServerConn
from flask import Flask, render_template, request, redirect, url_for, session, flash
import json, socket

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'    # Secret key para poder usar session

# Variables globales
msgHistory = None
username = None

@app.route("/", methods=['POST', 'GET'])
def login():
    if (request.method == 'POST'):
        data = {"action": "login",
                "username": request.form["username"],
                "password": request.form["password"],
                "port": port}
        response = sendData(json.dumps(data), socketClient)

        if response["success"]:
            # Session permite guardar variables en la sesión de un cliente
            global username
            if response["gender"] == 'male':
                session["imgUrl"] = '../static/images/male-icon.png'
            else:
                session["imgUrl"] = '../static/images/female-icon.png'
            session["username"] = data["username"]
            session["room"] = 'default'
            username = data["username"]
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
    global msgHistory
    msg = ''
    msgSentBy = ''

    if (request.method == 'POST'):
        if (request.is_json):
            # Este tipo de request se recibe directamente del servidor
            if request.get_json()["action"] == 'changeRoom':
                session["room"] = 'default'
            session["username"] = username
            msg = request.get_json()["msg"]
            msgSentBy = request.get_json()["username"]
        else:
            # En caso contrario es el request desde el form
            msg = request.form['message']
            data = {"action": "sendMsg",
                    "username": session["username"],
                    "msg": msg,}
            msgSentBy = data["username"]
            if msg:
                response = sendData(json.dumps(data), socketClient)
                if (response["action"] == "commandResult"):
                    session["room"] = response["room"]
                    msg = response["message"]
                    msgSentBy = "Sistema"
            
    if not msgHistory:
        msgHistory = []
        msgHistory.append(['Sistema', 'Puedes escribir #help para ver los comandos disponibles'])
    if msg and msgSentBy:
        msgHistory.append([msgSentBy, msg])
    return render_template("room.html", msgList=msgHistory, username=session["username"], 
                            room=session["room"], imgUrl=session["imgUrl"])

@app.route("/closeSession", methods=['POST', 'GET'])
def closeSession():
    global username, msgHistory
    user = username

    data = {"action": "close"}
    response = sendData(json.dumps(data), socketClient)
    
    # Se limpia la información en la sesión del cliente
    session.clear()
    username = None
    msgHistory = None

    socketClient.close()
    return render_template("closeSession.html", username=user)

if __name__ == "__main__":
    port = '5001'
    # Socket que se utiliza en el lado del cliente
    socketClient = socket.socket()
    socketClient.connect(("localhost", 8001))

    app.run(debug=False, port=port)