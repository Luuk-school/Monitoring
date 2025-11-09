from flask import Flask, render_template, jsonify, request
from MariaDB.connector import databaseConnection
from datetime import datetime, timezone


app = Flask(__name__, template_folder="Frontend")

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/api/sysdata', methods = ['POST'])
def api():
    if request.method == 'POST':
        req = request.get_json(force=True)

        # Minimal validation
        if not req:
            return jsonify({'status': 'error', 'message': 'no JSON payload'}), 400

        hostname = req.get('hostname')
        timestamp = req.get('timestamp')
        cpu_percent = req.get('cpu_percent')
        memory = req.get('memory', {})
        disk = req.get('disk', {})

        if not hostname or not timestamp:
            return jsonify({'status': 'error', 'message': 'missing hostname or timestamp'}), 400

        # Parse timestamp (ISO format). Convert to UTC naive datetime for MySQL DATETIME.
        try:
            collected_dt = datetime.fromisoformat(timestamp)
            if collected_dt.tzinfo is not None:
                collected_dt = collected_dt.astimezone(timezone.utc).replace(tzinfo=None)
        except Exception:
            # Fallback: try to parse without timezone
            try:
                collected_dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
            except Exception:
                # If parsing fails, use current UTC time
                collected_dt = datetime.utcnow()

        collected_at_str = collected_dt.strftime("%Y-%m-%d %H:%M:%S")

        insert_sql = (
            "INSERT INTO Systemdata (hostname, collected_at, cpu_percent, "
            "mem_total, mem_available, mem_used, mem_free, mem_percent, "
            "disk_total, disk_available, disk_used, disk_free, disk_percent) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )

        params = (
            hostname,
            collected_at_str,
            cpu_percent,
            memory.get('total'),
            memory.get('available'),
            memory.get('used'),
            memory.get('free'),
            memory.get('percent'),
            disk.get('total'),
            disk.get('available'),
            disk.get('used'),
            disk.get('free'),
            disk.get('percent'),
        )

        # Attempt DB insert. databaseConnection will print errors if it fails.
        try:
            databaseConnection(insert_sql, params)
            return jsonify({'status': 'success', 'stored': 'db'}), 201
        except Exception as e:
            # In practice connector prints errors and doesn't raise; still handle unexpected exceptions
            app.logger.error("Error storing sysdata: %s", e)
            return jsonify({'status': 'error', 'message': 'failed to store data'}), 500



        
        
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

