#!/usr/bin/env python3
"""
SSH-based monitoring voor remote servers
Geen monitoring software vereist op remote hosts
"""
import paramiko
import json
import time
from datetime import datetime

class SSHMonitor:
    def __init__(self, host_config):
        self.host_config = host_config
        self.ssh = None
        
    def connect(self):
        """Maak SSH verbinding"""
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            self.ssh.connect(
                hostname=self.host_config['ip'],
                username=self.host_config.get('ssh_user', 'monitoring'),
                password=self.host_config.get('ssh_password'),
                key_filename=self.host_config.get('ssh_key'),
                port=self.host_config.get('ssh_port', 22),
                timeout=10
            )
            return True
        except Exception as e:
            print(f"SSH connection failed: {e}")
            return False
    
    def execute_command(self, command):
        """Voer commando uit via SSH"""
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            
            if error:
                print(f"Command error: {error}")
                return None
            return output
        except Exception as e:
            print(f"Command execution failed: {e}")
            return None
    
    def get_system_info(self):
        """Haal systeem informatie op via SSH"""
        if not self.connect():
            return None
            
        try:
            data = {}
            
            # CPU informatie (Linux)
            if self.host_config.get('type') == 'linux':
                # CPU usage
                cpu_cmd = "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1"
                cpu_usage = self.execute_command(cpu_cmd)
                if cpu_usage:
                    data['cpu_usage'] = float(cpu_usage.replace(',', '.'))
                
                # Memory info
                mem_cmd = "free | grep Mem | awk '{printf \"%.1f\", $3/$2 * 100.0}'"
                mem_usage = self.execute_command(mem_cmd)
                if mem_usage:
                    data['memory_usage'] = float(mem_usage)
                
                # Disk usage
                disk_cmd = "df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1"
                disk_usage = self.execute_command(disk_cmd)
                if disk_usage:
                    data['disk_usage'] = float(disk_usage)
                
                # Uptime
                uptime_cmd = "uptime -p"
                uptime = self.execute_command(uptime_cmd)
                data['uptime'] = uptime
                
                # Hostname
                hostname_cmd = "hostname"
                hostname = self.execute_command(hostname_cmd)
                data['hostname'] = hostname
                
                # Process count
                process_cmd = "ps aux | wc -l"
                processes = self.execute_command(process_cmd)
                if processes:
                    data['process_count'] = int(processes) - 1
                    
            # Windows commando's
            elif self.host_config.get('type') == 'windows':
                # CPU usage (PowerShell)
                cpu_cmd = 'powershell "Get-Counter \'\\Processor(_Total)\\% Processor Time\' | Select-Object -ExpandProperty CounterSamples | Select-Object -ExpandProperty CookedValue"'
                cpu_usage = self.execute_command(cpu_cmd)
                if cpu_usage:
                    data['cpu_usage'] = float(cpu_usage)
                
                # Memory usage
                mem_cmd = 'powershell "(Get-WmiObject -Class Win32_OperatingSystem | % {[math]::Round(($_.TotalVisibleMemorySize - $_.FreePhysicalMemory)*100/$_.TotalVisibleMemorySize)})"'
                mem_usage = self.execute_command(mem_cmd)
                if mem_usage:
                    data['memory_usage'] = float(mem_usage)
            
            data['status'] = 'online'
            data['last_update'] = datetime.now().isoformat()
            
            return data
            
        except Exception as e:
            print(f"Failed to collect data: {e}")
            return None
        finally:
            if self.ssh:
                self.ssh.close()

# Voorbeeld configuratie
SSH_HOSTS = {
    'ubuntu-db': {
        'ip': '192.168.2.2',
        'type': 'linux',
        'ssh_user': 'monitoring',
        'ssh_password': 'your_password',  # Of gebruik SSH keys
        # 'ssh_key': '/path/to/private/key'
    },
    'windows-ad': {
        'ip': '192.168.2.1', 
        'type': 'windows',
        'ssh_user': 'Administrator',
        'ssh_password': 'your_password'
    }
}

if __name__ == "__main__":
    # Test SSH monitoring
    for host_id, config in SSH_HOSTS.items():
        print(f"Testing {host_id}...")
        monitor = SSHMonitor(config)
        data = monitor.get_system_info()
        print(f"Result: {json.dumps(data, indent=2)}")