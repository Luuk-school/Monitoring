from flask import Flask, render_template, jsonify, request
from MariaDB.connector import databaseConnection

app = Flask(__name__, template_folder="Frontend")

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/api/data', methods = ['GET', 'POST'])
def api():
    if(request.method == 'GET'):

        data = "hello world"
        return jsonify({'data': data})
        
@app.route('/api/agentInfo', methods = ['POST'])
def agent_info():
    if(request.method == 'POST'):
        data = request.json
        print("Received agent info:", data)
        sql = "INSERT INTO agent (ComputerName, IP, Version) VALUES (%s, %s, %s)"
        parameters = (data['ComputerName'], data['IP'], data['Version'])
        databaseConnection(sql, parameters)
        return jsonify({'status': 'success'})

