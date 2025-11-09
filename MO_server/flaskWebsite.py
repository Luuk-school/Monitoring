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
def agent_info(): #agent information checker
    if(request.method == 'POST'):
        req = request.json
        print("Received agent info:", req)

        # SQL statements
        insert_sql = "INSERT INTO agent (ComputerName, IP, Version) VALUES (%s, %s, %s)"
        insert_params = (req['ComputerName'], req['IP'], req['Version'])

        update_sql = "UPDATE agent SET IP = %s, Version = %s WHERE ComputerName = %s"
        update_params = (req['IP'], req['Version'], req['ComputerName'])

        check_version_sql = "SELECT Version FROM agent WHERE ComputerName = %s"
        rows = databaseConnection(check_version_sql, (req['ComputerName'],))

        if rows and len(rows) > 0:  #ai
            current_version = rows[0][0]
            # computer exists
            if current_version != req['Version']:
                # update
                ##### send update request to agent manager.  ####    ==== hier moet je nog werke =====
                databaseConnection(update_sql, update_params)
                return jsonify({'status': 'updated', 'old_version': current_version, 'new_version': req['Version']})
            else:
                # versions match
                return jsonify({'status': 'no_change', 'version': current_version})
        else:
            # computer does not exist — insert it
            databaseConnection(insert_sql, insert_params)
            return jsonify({'status': 'inserted', 'version': req['Version']})

