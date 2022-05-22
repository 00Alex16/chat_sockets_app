from utils.socketClient import sendData
from utils.ServerConn import ServerConn
from flask import Flask, render_template, request, redirect, url_for, session
import json, socket

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'    # Secret key para poder usar session

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
            session["username"] = data["username"]
            session["room"] = 'default'
            username = data["username"]
            # Se inicia hilo para recibir los mensajes de otros clientes
            #msgListening = ServerConn(socketClient, data["username"])
            #msgListening.start()

            return redirect(url_for('chat'))

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
        response = sendData(json.dumps(data))
        print(response)

    return render_template("register.html")

@app.route("/chat", methods=['POST', 'GET'])
def chat():
    global msgHistory
    msg = ''
    msgSentBy = ''
    if (request.method == 'POST'):
        if (request.is_json):
            session["username"] = username
            msg = request.get_json()["msg"]
            msgSentBy = request.get_json()["username"]
        else:
            msg = request.form['message']
            data = {"action": "sendMsg",
                    "username": session["username"],
                    "msg": msg,}
            msgSentBy = data["username"]
            if msg:
                response = sendData(json.dumps(data), socketClient)
                print("ANTES CONDS", response)
                if (response["action"] == "msgResult"):
                    print("MSG",response)
                elif (response["action"] == "commandResult"):
                    session["room"] = response["room"]
                    msg = response["message"]
                    msgSentBy = "Sistema"
                    print("COMMAND",response)
            
    if not msgHistory:
        msgHistory = []
    if msg and msgSentBy:
        msgHistory.append([msgSentBy, msg])
    print(msgHistory, session["room"])
    return render_template("room.html", msgList=msgHistory, username=session["username"], room=session["room"])

@app.route("/closeSession", methods=['POST', 'GET'])
def closeSession():
    global username, msgHistory
    if (request.method == 'POST'):
        data = {"action": "close"}
        response = sendData(json.dumps(data), socketClient)
        
        # Se limpia la información en la sesión del cliente
        session.clear()
        username = None
        msgHistory = None

        socketClient.close()
        return render_template("closeSession.html")

if __name__ == "__main__":
    # Socket que se utiliza en el lado del cliente
    port = '5001'
    socketClient = socket.socket()
    socketClient.connect(("localhost", 8001))

    app.run(debug=False, port=port)