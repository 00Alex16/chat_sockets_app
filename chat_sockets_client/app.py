from utils.socketClient import sendData
from flask import Flask
from flask import render_template
from flask import request
import json

app = Flask(__name__)

@app.route("/", methods=['POST', 'GET'])
def login():
    if (request.method == 'POST'):
        data = {"action": "login",
                "username": request.form["username"],
                "password": request.form["password"]}
        response = sendData(json.dumps(data))
        print(response)
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

if __name__ == "__main__":
    app.run(debug=True, port='5001')