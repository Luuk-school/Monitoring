#!/usr/bin/env python3
"""
Lightweight monitoring agent
Een zeer klein script voor op elke remote server
"""
import psutil
import json
import socket
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

class MonitoringHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/data':
            try:
                # Verzamel basis systeem informatie
                data = {
                    'cpu': {
                        'usage_percent': psutil.cpu_percent(interval=1),
                        'core_count': psutil.cpu_count()
                    },
                    'memory': {
                        'usage_percent': psutil.virtual_memory().percent,
                        'total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                        'used_gb': round(psutil.virtual_memory().used / (1024**3), 2)
                    },
                    'disk': {
                        'usage_percent': psutil.disk_usage('/').percent,
                        'total_gb': round(psutil.disk_usage('/').total / (1024**3), 2),
                        'used_gb': round(psutil.disk_usage('/').used / (1024**3), 2)
                    },
                    'system': {
                        'hostname': socket.gethostname(),
                        'uptime_days': 0,  # Simplified
                        'users_count': len(psutil.users())
                    },
                    'processes': [
                        {'pid': p.info['pid'], 'name': p.info['name'][:20], 
                         'cpu_percent': p.info['cpu_percent'], 'memory_percent': p.info['memory_percent']}
                        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent'])
                    ][:10]
                }
                
                response = {
                    'success': True,
                    'data': data
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = {'success': False, 'error': str(e)}
                self.wfile.write(json.dumps(error_response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default logging
        return

if __name__ == "__main__":
    PORT = 5000
    print(f"Starting lightweight monitoring agent on port {PORT}")
    
    httpd = HTTPServer(('0.0.0.0', PORT), MonitoringHandler)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Stopping agent...")
        httpd.shutdown()