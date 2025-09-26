from flask import Flask, render_template, jsonify
from monitor import SystemMonitor
import config
import json

app = Flask(__name__)
monitor = SystemMonitor()

@app.route('/')
def index():
    """Hoofdpagina met system monitoring dashboard"""
    try:
        # Verzamel alle system data
        data = monitor.collect_current_data()
        
        # Controleer voor alerts
        alerts = monitor.get_alerts(data)
        
        return render_template('index.html',
                             cpu_info=data['cpu'],
                             memory_info=data['memory'], 
                             disk_info=data['disk'],
                             network_info=data['network'],
                             processes=data['processes'],
                             system_info=data['system'],
                             history=monitor.history,
                             alerts=alerts,
                             config=config)
    except Exception as e:
        print(f"Fout bij het verzamelen van data: {e}")
        return f"Error: {e}", 500

@app.route('/api/data')
def get_data():
    """API endpoint voor JSON data"""
    try:
        data = monitor.collect_current_data()
        alerts = monitor.get_alerts(data)
        
        return jsonify({
            'success': True,
            'data': data,
            'history': monitor.history,
            'alerts': alerts
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/history')
def get_history():
    """API endpoint voor historische data"""
    return jsonify(monitor.history)

@app.template_filter('tojsonfilter')
def to_json_filter(obj):
    """Custom Jinja2 filter om Python objecten naar JSON te converteren"""
    return json.dumps(obj)

if __name__ == '__main__':
    print("🚀 Starting System Monitor...")
    print(f"📊 Dashboard beschikbaar op: http://{config.HOST}:{config.PORT}")
    print(f"🔄 Auto-refresh interval: {config.REFRESH_INTERVAL} seconden")
    print("⚡ Gebruik Ctrl+C om te stoppen")
    
    app.run(host=config.HOST, 
            port=config.PORT, 
            debug=config.DEBUG)
