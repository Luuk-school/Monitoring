from flask import Flask, render_template, jsonify, request
from monitor import SystemMonitor
from hybrid_monitor import HybridMultiHostMonitor
from log_reader import log_reader
from datetime import datetime
import config
import json

app = Flask(__name__)
monitor = SystemMonitor()
multi_monitor = HybridMultiHostMonitor()

@app.route('/')
def index():
    """Multi-host monitoring dashboard"""
    try:
        print(f"🌐 DEBUG: Dashboard requested at {datetime.now().strftime('%H:%M:%S')}")
        
        # Update alle hosts data
        multi_monitor.update_all_hosts()
        
        # Krijg samenvatting van alle hosts
        hosts_summary = multi_monitor.get_all_hosts_summary()
        overall_status = multi_monitor.get_overall_status()
        
        print(f"🌐 DEBUG: Dashboard data collected - {overall_status['online']}/{overall_status['total']} hosts online")
        
        return render_template('dashboard.html',
                             hosts=hosts_summary,
                             overall_status=overall_status,
                             config=config)
    except Exception as e:
        print(f"❌ DEBUG: Error collecting multi-host data in dashboard: {e}")
        return f"Error: {e}", 500

@app.route('/host/<host_id>')
def host_detail(host_id):
    """Gedetailleerde view van een specifieke host"""
    try:
        print(f"🖥️ DEBUG: Host detail requested for {host_id}")
        
        if host_id not in config.MONITORED_HOSTS:
            print(f"❌ DEBUG: Host {host_id} not found in configuration")
            return "Host niet gevonden", 404
            
        # Update data voor specifieke host
        data = multi_monitor.get_host_data(host_id)
        
        if not data:
            print(f"⚠️ DEBUG: No data available for host {host_id}, status: {multi_monitor.hosts_status.get(host_id)}")
            return render_template('host_offline.html', 
                                 host_id=host_id,
                                 host_info=config.MONITORED_HOSTS[host_id],
                                 status=multi_monitor.hosts_status.get(host_id))
        
        # Controleer voor alerts
        alerts = multi_monitor.get_host_alerts(data)
        print(f"🖥️ DEBUG: Host {host_id} data collected successfully, {len(alerts)} alerts")
        
        return render_template('host_detail.html',
                             host_id=host_id,
                             host_info=config.MONITORED_HOSTS[host_id],
                             cpu_info=data['cpu'],
                             memory_info=data['memory'], 
                             disk_info=data['disk'],
                             network_info=data['network'],
                             processes=data['processes'],
                             system_info=data['system'],
                             alerts=alerts,
                             config=config)
    except Exception as e:
        print(f"Fout bij het verzamelen van host data voor {host_id}: {e}")
        return f"Error: {e}", 500



@app.route('/api/data')
def get_data():
    """API endpoint voor JSON data (legacy - single host)"""
    try:
        print(f"🔌 DEBUG: API data request received from client")
        data = monitor.collect_current_data()
        alerts = monitor.get_alerts(data)
        print(f"🔌 DEBUG: API data response sent, {len(alerts)} alerts")
        
        return jsonify({
            'success': True,
            'data': data,
            'history': monitor.history,
            'alerts': alerts
        })
    except Exception as e:
        print(f"❌ DEBUG: Error in API data endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hosts')
def get_all_hosts():
    """API endpoint voor alle hosts data"""
    try:
        print(f"🔌 DEBUG: API hosts request received, updating all hosts...")
        multi_monitor.update_all_hosts()
        hosts_summary = multi_monitor.get_all_hosts_summary()
        print(f"🔌 DEBUG: API hosts response ready, returning {len(hosts_summary)} hosts")
        overall_status = multi_monitor.get_overall_status()
        
        return jsonify({
            'success': True,
            'hosts': hosts_summary,
            'overall_status': overall_status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/host/<host_id>')
def get_host_data(host_id):
    """API endpoint voor specifieke host data"""
    try:
        print(f"🔌 DEBUG: API request for specific host: {host_id}")
        
        if host_id not in config.MONITORED_HOSTS:
            print(f"❌ DEBUG: API request for unknown host: {host_id}")
            return jsonify({
                'success': False,
                'error': 'Host not found'
            }), 404
            
        data = multi_monitor.get_host_data(host_id)
        status = multi_monitor.hosts_status.get(host_id, 'unknown')
        
        print(f"🔌 DEBUG: API response for {host_id} - status: {status}, has_data: {data is not None}")
        
        return jsonify({
            'success': True,
            'host_id': host_id,
            'host_info': config.MONITORED_HOSTS[host_id],
            'status': status,
            'data': data,
            'last_update': multi_monitor.last_update.get(host_id).isoformat() if multi_monitor.last_update.get(host_id) else None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/logs')
def logs_viewer():
    """Live log viewer pagina"""
    try:
        # Get available hosts and log types for filters
        log_stats = log_reader.get_log_stats()
        hosts_summary = multi_monitor.get_all_hosts_summary()
        
        return render_template('logs.html',
                             log_stats=log_stats,
                             hosts=hosts_summary,
                             config=config)
    except Exception as e:
        print(f"Fout bij log viewer: {e}")
        return f"Error: {e}", 500

@app.route('/api/logs')
def get_logs():
    """API endpoint voor log data"""
    try:
        host_id = request.args.get('host_id')
        log_type = request.args.get('log_type')
        limit = int(request.args.get('limit', 100))
        level_filter = request.args.get('level')
        
        logs = log_reader.get_logs(
            host_id=host_id,
            log_type=log_type,
            limit=limit,
            level_filter=level_filter
        )
        
        return jsonify({
            'success': True,
            'logs': logs,
            'stats': log_reader.get_log_stats()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/retry/<host_id>', methods=['POST'])
def retry_host_connection(host_id):
    """API endpoint to retry connection to a specific host"""
    try:
        print(f"🔄 DEBUG: Retry connection requested for host: {host_id}")
        
        if host_id not in config.MONITORED_HOSTS:
            print(f"❌ DEBUG: Retry request for unknown host: {host_id}")
            log_reader.add_manual_log(host_id, 'connection', f'Retry failed: Host {host_id} not found in configuration', 'ERROR')
            return jsonify({
                'success': False,
                'error': 'Host not found'
            }), 404
        
        host_info = config.MONITORED_HOSTS[host_id]
        log_reader.add_manual_log(host_id, 'connection', f'Connection retry initiated for {host_info["name"]} ({host_info["ip"]})', 'INFO')
        
        # Get current status before retry
        old_status = multi_monitor.hosts_status.get(host_id, 'unknown')
        
        # Force update for this specific host
        print(f"🔄 DEBUG: Forcing update for host {host_id}")
        data = multi_monitor.get_host_data(host_id)
        new_status = multi_monitor.hosts_status.get(host_id, 'unknown')
        
        # Log the result
        status_messages = {
            'online': f'✅ Connection retry successful! Host {host_info["name"]} is now online. Status: {old_status} → {new_status}',
            'offline': f'❌ Connection retry failed: Host {host_info["name"]} ({host_info["ip"]}:{host_info["port"]}) is still offline. Connection refused or host unreachable.',
            'timeout': f'⏰ Connection retry failed: Host {host_info["name"]} ({host_info["ip"]}:{host_info["port"]}) timed out. Connection timeout after {config.CONNECTION_TIMEOUT}s or request timeout after {config.REQUEST_TIMEOUT}s.',
            'error': f'🚨 Connection retry error: Host {host_info["name"]} ({host_info["ip"]}:{host_info["port"]}) encountered an error during connection attempt.',
            'unknown': f'⚠️ Connection retry completed with unknown status for host {host_info["name"]}'
        }
        
        log_levels = {
            'online': 'SUCCESS',
            'offline': 'WARNING',
            'timeout': 'WARNING', 
            'error': 'ERROR',
            'unknown': 'WARNING'
        }
        
        message = status_messages.get(new_status, status_messages['unknown'])
        level = log_levels.get(new_status, 'WARNING')
        log_reader.add_manual_log(host_id, 'connection', message, level)
        
        print(f"🔄 DEBUG: Retry result for {host_id} - status: {old_status} → {new_status}, has_data: {data is not None}")
        
        return jsonify({
            'success': True,
            'host_id': host_id,
            'status': new_status,
            'has_data': data is not None,
            'old_status': old_status,
            'message': f'Connection retry completed for {host_info["name"]}'
        })
    except Exception as e:
        print(f"❌ DEBUG: Error during retry for {host_id}: {e}")
        log_reader.add_manual_log(host_id, 'connection', 
            f'🚨 Connection retry failed with exception: {str(e)}', 'ERROR')
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
