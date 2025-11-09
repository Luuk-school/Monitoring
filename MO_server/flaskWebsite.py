from flask import Flask, render_template, jsonify, request
from MariaDB.connector import databaseConnection
from datetime import datetime, timezone


app = Flask(__name__, template_folder="Frontend", static_folder="Frontend")

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



@app.route('/latest_sysdata', methods=['GET'])
def latest_sysdata():
    """Return latest sysdata per hostname by reading the database.

    This queries the Systemdata table for the most recent collected_at per
    hostname and returns an array of records shaped like the original POST payload.
    """
    # SQL: select latest row per hostname
    latest_sql = (
        "SELECT s.hostname, s.collected_at, s.cpu_percent, "
        "s.mem_total, s.mem_available, s.mem_used, s.mem_free, s.mem_percent, "
        "s.disk_total, s.disk_available, s.disk_used, s.disk_free, s.disk_percent "
        "FROM Systemdata s "
        "JOIN (SELECT hostname, MAX(collected_at) AS maxcol FROM Systemdata GROUP BY hostname) m "
        "ON s.hostname = m.hostname AND s.collected_at = m.maxcol"
    )

    try:
        rows = databaseConnection(latest_sql)
    except Exception as e:
        app.logger.error('Error querying latest sysdata: %s', e)
        return jsonify({'status': 'error', 'message': 'db query failed'}), 500

    if not rows:
        # No data yet
        return jsonify([]), 200

    results = []
    for r in rows:
        # r is expected to be a tuple matching the selected columns
        (
            hostname, collected_at, cpu_percent,
            mem_total, mem_available, mem_used, mem_free, mem_percent,
            disk_total, disk_available, disk_used, disk_free, disk_percent
        ) = r

        record = {
            'hostname': hostname,
            'timestamp': collected_at.strftime("%Y-%m-%dT%H:%M:%S") if hasattr(collected_at, 'strftime') else str(collected_at),
            'cpu_percent': cpu_percent,
            'memory': {
                'total': mem_total,
                'available': mem_available,
                'used': mem_used,
                'free': mem_free,
                'percent': mem_percent,
            },
            'disk': {
                'total': disk_total,
                'available': disk_available,
                'used': disk_used,
                'free': disk_free,
                'percent': disk_percent,
            }
        }
        results.append(record)

    return jsonify(results), 200



        
        
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

