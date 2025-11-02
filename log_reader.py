import os
import time
import threading
from datetime import datetime
from collections import defaultdict, deque
import re

class LogReader:
    def __init__(self, max_lines=1000):
        self.max_lines = max_lines
        self.logs = defaultdict(lambda: deque(maxlen=max_lines))
        self.log_files = {}
        self.monitoring = False
        self.monitor_thread = None
        
        # Common log file locations per OS type
        self.log_paths = {
            'linux': [
                '/var/log/syslog',
                '/var/log/messages',
                '/var/log/auth.log',
                '/var/log/apache2/access.log',
                '/var/log/apache2/error.log',
                '/var/log/nginx/access.log',
                '/var/log/nginx/error.log',
                '/var/log/mysql/error.log',
                '/var/log/postgresql/postgresql.log'
            ],
            'windows': [
                'C:\\Windows\\System32\\LogFiles\\HTTPERR\\httperr1.log',
                'C:\\inetpub\\logs\\LogFiles\\W3SVC1\\*.log',
            ]
        }
        
        self.start_monitoring()
    
    def get_available_log_files(self, host_type='linux'):
        """Get list of available log files for a host type"""
        available = []
        paths = self.log_paths.get(host_type, self.log_paths['linux'])
        
        for path in paths:
            if '*' in path:
                # Handle wildcard paths
                import glob
                matching_files = glob.glob(path)
                for file in matching_files:
                    if os.path.exists(file) and os.access(file, os.R_OK):
                        available.append(file)
            else:
                if os.path.exists(path) and os.access(path, os.R_OK):
                    available.append(path)
        
        return available
    
    def add_log_file(self, host_id, file_path, log_type='system'):
        """Add a log file to monitor for a specific host"""
        if os.path.exists(file_path) and os.access(file_path, os.R_OK):
            key = f"{host_id}:{log_type}"
            self.log_files[key] = {
                'path': file_path,
                'host_id': host_id,
                'log_type': log_type,
                'last_position': 0,
                'last_modified': 0
            }
            return True
        return False
    
    def start_monitoring(self):
        """Start the log monitoring thread"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_logs, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop the log monitoring thread"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitor_logs(self):
        """Background thread to monitor log files for changes"""
        while self.monitoring:
            try:
                for key, log_info in self.log_files.items():
                    self._read_log_updates(key, log_info)
                time.sleep(1)  # Check every second
            except Exception as e:
                print(f"Log monitoring error: {e}")
                time.sleep(5)
    
    def _read_log_updates(self, key, log_info):
        """Read new lines from a log file"""
        try:
            file_path = log_info['path']
            if not os.path.exists(file_path):
                return
            
            # Check if file was modified
            current_modified = os.path.getmtime(file_path)
            if current_modified <= log_info['last_modified']:
                return
            
            log_info['last_modified'] = current_modified
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Seek to last position
                f.seek(log_info['last_position'])
                
                new_lines = f.readlines()
                if new_lines:
                    # Update position
                    log_info['last_position'] = f.tell()
                    
                    # Process new lines
                    for line in new_lines:
                        line = line.strip()
                        if line:
                            log_entry = {
                                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'host_id': log_info['host_id'],
                                'log_type': log_info['log_type'],
                                'message': line,
                                'level': self._detect_log_level(line)
                            }
                            self.logs[key].append(log_entry)
        
        except Exception as e:
            print(f"Error reading log file {file_path}: {e}")
    
    def add_manual_log(self, host_id, log_type, message, level='INFO'):
        """Manually add a log entry to the log viewer"""
        try:
            key = f"{host_id}:{log_type}"
            log_entry = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'host_id': host_id,
                'log_type': log_type,
                'message': message,
                'level': level
            }
            self.logs[key].append(log_entry)
            print(f" Added manual log: {host_id}:{log_type} - {message}")
        except Exception as e:
            print(f"Error adding manual log: {e}")
    
    def _detect_log_level(self, message):
        """Detect log level from message content"""
        message_upper = message.upper()
        if any(word in message_upper for word in ['✅', 'SUCCESS', 'SUCCESSFUL', 'ONLINE', 'CONNECTED']):
            return 'success'
        elif any(word in message_upper for word in ['ERROR', 'FATAL', 'CRITICAL', '❌', '🚨']):
            return 'error'
        elif any(word in message_upper for word in ['WARN', 'WARNING', '⚠️', '⏰']):
            return 'warning'
        elif any(word in message_upper for word in ['INFO', 'INFORMATION']):
            return 'info'
        elif any(word in message_upper for word in ['DEBUG', 'TRACE']):
            return 'debug'
        else:
            return 'info'
    
    def get_logs(self, host_id=None, log_type=None, limit=100, level_filter=None):
        """Get logs with optional filtering"""
        result = []
        
        for key, log_entries in self.logs.items():
            # Parse key
            key_host_id, key_log_type = key.split(':', 1)
            
            # Apply filters
            if host_id and key_host_id != host_id:
                continue
            if log_type and key_log_type != log_type:
                continue
            
            # Get recent entries
            for entry in list(log_entries):
                if level_filter and entry['level'] != level_filter:
                    continue
                result.append(entry)
        
        # Sort by timestamp (newest first) and limit
        result.sort(key=lambda x: x['timestamp'], reverse=True)
        return result[:limit]
    
    def get_log_stats(self):
        """Get statistics about monitored logs"""
        stats = {
            'total_files': len(self.log_files),
            'total_entries': sum(len(entries) for entries in self.logs.values()),
            'hosts': set(),
            'log_types': set()
        }
        
        for key in self.log_files.keys():
            host_id, log_type = key.split(':', 1)
            stats['hosts'].add(host_id)
            stats['log_types'].add(log_type)
        
        stats['hosts'] = list(stats['hosts'])
        stats['log_types'] = list(stats['log_types'])
        
        return stats

# Global log reader instance
log_reader = LogReader()

# Add some default log files for localhost with fallbacks
default_logs = [
    ('/var/log/syslog', 'system'),
    ('/var/log/auth.log', 'auth'),
    ('/var/log/apache2/access.log', 'apache_access'),
    ('/var/log/apache2/error.log', 'apache_error'),
    ('/var/log/nginx/access.log', 'nginx_access'),
    ('/var/log/nginx/error.log', 'nginx_error'),
]

for log_path, log_type in default_logs:
    if os.path.exists(log_path) and os.access(log_path, os.R_OK):
        log_reader.add_log_file('localhost', log_path, log_type)

# Fallback: add a demo log if no real logs are accessible
if not log_reader.log_files:
    # Create a simple demo log
    import tempfile
    demo_log_path = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log').name
    with open(demo_log_path, 'w') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} INFO System monitor started\n")
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} INFO No system logs accessible, using demo mode\n")
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WARNING This is demonstration data\n")
    
    log_reader.add_log_file('localhost', demo_log_path, 'demo')