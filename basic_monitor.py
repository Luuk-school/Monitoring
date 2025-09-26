#!/usr/bin/env python3
"""
Basic ping en service check monitoring
Geen software installatie vereist op remote hosts
"""
import subprocess
import socket
import time
from datetime import datetime

class BasicMonitor:
    def __init__(self, host_config):
        self.host_config = host_config
    
    def ping_host(self):
        """Ping test voor host bereikbaarheid"""
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '3', self.host_config['ip']], 
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def check_port(self, port, timeout=5):
        """Check of een specifieke poort open is"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((self.host_config['ip'], port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def check_services(self):
        """Check belangrijke services"""
        services = {
            'ssh': 22,
            'http': 80,
            'https': 443,
            'rdp': 3389,  # Windows RDP
            'smb': 445,   # Windows SMB
            'mysql': 3306,
            'postgresql': 5432,
            'monitoring': 5000
        }
        
        service_status = {}
        for service, port in services.items():
            service_status[service] = self.check_port(port)
        
        return service_status
    
    def get_basic_info(self):
        """Haal basis informatie op"""
        data = {
            'host_id': self.host_config.get('name', 'unknown'),
            'ip': self.host_config['ip'],
            'ping_success': self.ping_host(),
            'services': self.check_services(),
            'last_check': datetime.now().isoformat()
        }
        
        # Bepaal overall status
        if data['ping_success']:
            if data['services'].get('monitoring', False):
                data['status'] = 'monitoring_available'
            elif any(data['services'].values()):
                data['status'] = 'online_basic'
            else:
                data['status'] = 'online_no_services'
        else:
            data['status'] = 'offline'
        
        return data

# Test alle hosts
if __name__ == "__main__":
    hosts = [
        {'name': 'Windows AD', 'ip': '192.168.2.1'},
        {'name': 'Ubuntu DB', 'ip': '192.168.2.2'}, 
        {'name': 'Ubuntu Web', 'ip': '192.168.2.3'}
    ]
    
    for host_config in hosts:
        print(f"\nChecking {host_config['name']} ({host_config['ip']})...")
        monitor = BasicMonitor(host_config)
        info = monitor.get_basic_info()
        
        print(f"Status: {info['status']}")
        print(f"Ping: {'✓' if info['ping_success'] else '✗'}")
        print("Services:")
        for service, available in info['services'].items():
            if available:
                print(f"  {service}: ✓")
        print(f"Last check: {info['last_check']}")