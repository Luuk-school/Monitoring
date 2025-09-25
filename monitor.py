import psutil
import time
import json
import platform
import socket
from datetime import datetime
from config import MAX_HISTORY_POINTS

class SystemMonitor:
    def __init__(self):
        self.history = {
            'cpu': [],
            'memory': [],
            'disk': [],
            'network': [],
            'timestamps': []
        }
    
    def get_cpu_info(self):
        """Verzamel CPU informatie"""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        return {
            'usage_percent': cpu_percent,
            'core_count': cpu_count,
            'frequency_mhz': cpu_freq.current if cpu_freq else 0
        }
    
    def get_memory_info(self):
        """Verzamel geheugen informatie"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total_gb': round(memory.total / (1024**3), 2),
            'available_gb': round(memory.available / (1024**3), 2),
            'used_gb': round(memory.used / (1024**3), 2),
            'usage_percent': memory.percent,
            'swap_total_gb': round(swap.total / (1024**3), 2),
            'swap_used_gb': round(swap.used / (1024**3), 2),
            'swap_percent': swap.percent
        }
    
    def get_disk_info(self):
        """Verzamel disk informatie"""
        disk_usage = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        disk_info = {
            'total_gb': round(disk_usage.total / (1024**3), 2),
            'used_gb': round(disk_usage.used / (1024**3), 2),
            'free_gb': round(disk_usage.free / (1024**3), 2),
            'usage_percent': round((disk_usage.used / disk_usage.total) * 100, 2)
        }
        
        if disk_io:
            disk_info.update({
                'read_mb': round(disk_io.read_bytes / (1024**2), 2),
                'write_mb': round(disk_io.write_bytes / (1024**2), 2)
            })
        
        return disk_info
    
    def get_network_info(self):
        """Verzamel netwerk informatie"""
        net_io = psutil.net_io_counters()
        net_connections = len(psutil.net_connections())
        
        return {
            'bytes_sent_mb': round(net_io.bytes_sent / (1024**2), 2),
            'bytes_recv_mb': round(net_io.bytes_recv / (1024**2), 2),
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'active_connections': net_connections
        }
    
    def get_process_info(self):
        """Verzamel proces informatie"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sorteer op CPU gebruik
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        return processes[:10]  # Top 10 processen
    
    def get_system_info(self):
        """Verzamel basis systeem informatie"""
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        # Use platform module instead of psutil.uname() for better compatibility
        try:
            hostname = socket.gethostname()
        except:
            hostname = "Unknown"
            
        return {
            'hostname': hostname,
            'platform': platform.system(),
            'architecture': platform.machine(),
            'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S'),
            'uptime_days': uptime.days,
            'uptime_hours': uptime.seconds // 3600,
            'users_count': len(psutil.users())
        }
    
    def collect_current_data(self):
        """Verzamel alle huidige system data"""
        current_time = datetime.now()
        
        data = {
            'timestamp': current_time.strftime('%H:%M:%S'),
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'disk': self.get_disk_info(),
            'network': self.get_network_info(),
            'processes': self.get_process_info(),
            'system': self.get_system_info()
        }
        
        # Voeg toe aan geschiedenis
        self.add_to_history(data)
        
        return data
    
    def add_to_history(self, data):
        """Voeg data toe aan geschiedenis voor grafieken"""
        self.history['cpu'].append(data['cpu']['usage_percent'])
        self.history['memory'].append(data['memory']['usage_percent'])
        self.history['disk'].append(data['disk']['usage_percent'])
        self.history['network'].append(data['network']['bytes_sent_mb'] + data['network']['bytes_recv_mb'])
        self.history['timestamps'].append(data['timestamp'])
        
        # Beperk geschiedenis grootte
        for key in self.history:
            if len(self.history[key]) > MAX_HISTORY_POINTS:
                self.history[key] = self.history[key][-MAX_HISTORY_POINTS:]
    
    def get_alerts(self, data):
        """Controleer voor waarschuwingen"""
        from config import CPU_WARNING_THRESHOLD, MEMORY_WARNING_THRESHOLD, DISK_WARNING_THRESHOLD
        
        alerts = []
        
        if data['cpu']['usage_percent'] > CPU_WARNING_THRESHOLD:
            alerts.append({
                'type': 'warning',
                'message': f'CPU gebruik is hoog: {data["cpu"]["usage_percent"]}%'
            })
        
        if data['memory']['usage_percent'] > MEMORY_WARNING_THRESHOLD:
            alerts.append({
                'type': 'warning', 
                'message': f'Geheugen gebruik is hoog: {data["memory"]["usage_percent"]}%'
            })
        
        if data['disk']['usage_percent'] > DISK_WARNING_THRESHOLD:
            alerts.append({
                'type': 'danger',
                'message': f'Disk ruimte is kritiek: {data["disk"]["usage_percent"]}%'
            })
        
        return alerts