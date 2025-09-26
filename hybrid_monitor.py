#!/usr/bin/env python3
"""
Hybride Multi-Host Monitor
- Linux: SSH commands (geen Python installatie vereist)
- Windows: WMI/PowerShell over netwerk
- Fallback: Basic ping + port checks
"""
import subprocess
import socket
import time
import threading
import json
import re
from datetime import datetime
from config import MONITORED_HOSTS, CONNECTION_TIMEOUT, REQUEST_TIMEOUT

class HybridMultiHostMonitor:
    def __init__(self):
        from monitor import SystemMonitor
        self.local_monitor = SystemMonitor()
        self.hosts_data = {}
        self.hosts_status = {}
        self.last_update = {}
        
        # Initialize status voor alle hosts
        for host_id, host_info in MONITORED_HOSTS.items():
            self.hosts_status[host_id] = 'unknown'
            self.hosts_data[host_id] = None
            self.last_update[host_id] = None

    def is_localhost(self, host_id):
        """Check of dit de localhost is"""
        host_info = MONITORED_HOSTS.get(host_id)
        if not host_info:
            return False
        return host_info['ip'] in ['192.168.2.5', '127.0.0.1', 'localhost']

    def ping_host(self, ip):
        """Test of host bereikbaar is via ping"""
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '3', ip], 
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    def check_port(self, ip, port, timeout=3):
        """Check of specifieke poort open is"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def get_linux_data_via_ssh(self, host_info):
        """Haal Linux data op via SSH commands"""
        ip = host_info['ip']
        ssh_user = host_info.get('ssh_user', 'root')
        
        try:
            # Test SSH connectivity first
            ssh_test = subprocess.run([
                'ssh', '-o', 'ConnectTimeout=5', '-o', 'StrictHostKeyChecking=no',
                f'{ssh_user}@{ip}', 'echo "connected"'
            ], capture_output=True, text=True, timeout=10)
            
            if ssh_test.returncode != 0:
                print(f"SSH connection failed to {ip}: {ssh_test.stderr}")
                return None

            # Collect system data via SSH
            commands = {
                'cpu_usage': "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | sed 's/%us,//'",
                'memory_usage': "free | grep Mem | awk '{printf \"%.1f\", $3/$2 * 100.0}'",
                'disk_usage': "df -h / | awk 'NR==2 {print $5}' | sed 's/%//'",
                'hostname': "hostname",
                'uptime': "uptime -p",
                'process_count': "ps aux | wc -l",
                'load_avg': "uptime | awk -F'load average:' '{print $2}' | cut -d, -f1",
                'memory_total': "free -m | grep Mem | awk '{print $2}'",
                'disk_total': "df -BG / | awk 'NR==2 {print $2}' | sed 's/G//'"
            }
            
            data = {}
            for key, command in commands.items():
                try:
                    result = subprocess.run([
                        'ssh', '-o', 'ConnectTimeout=5', '-o', 'StrictHostKeyChecking=no',
                        f'{ssh_user}@{ip}', command
                    ], capture_output=True, text=True, timeout=8)
                    
                    if result.returncode == 0:
                        value = result.stdout.strip()
                        if key in ['cpu_usage', 'memory_usage', 'disk_usage']:
                            try:
                                data[key] = float(value.replace(',', '.'))
                            except ValueError:
                                data[key] = 0.0
                        elif key in ['process_count', 'memory_total', 'disk_total']:
                            try:
                                data[key] = int(value)
                            except ValueError:
                                data[key] = 0
                        else:
                            data[key] = value
                    else:
                        data[key] = None
                        print(f"SSH command failed for {key}: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    print(f"SSH command timeout for {key}")
                    data[key] = None
            
            # Format data in expected structure
            formatted_data = {
                'cpu': {
                    'usage_percent': data.get('cpu_usage', 0),
                    'core_count': 1,  # Could get via nproc command
                    'frequency_mhz': 0
                },
                'memory': {
                    'usage_percent': data.get('memory_usage', 0),
                    'total_gb': round(data.get('memory_total', 0) / 1024, 2) if data.get('memory_total') else 0,
                    'used_gb': 0,
                    'available_gb': 0
                },
                'disk': {
                    'usage_percent': data.get('disk_usage', 0),
                    'total_gb': data.get('disk_total', 0),
                    'used_gb': 0,
                    'free_gb': 0
                },
                'network': {
                    'bytes_sent_mb': 0,
                    'bytes_recv_mb': 0,
                    'packets_sent': 0,
                    'packets_recv': 0,
                    'active_connections': 0
                },
                'processes': [
                    {'pid': 0, 'name': 'ssh-data', 'cpu_percent': 0, 'memory_percent': 0}
                ],
                'system': {
                    'hostname': data.get('hostname', 'unknown'),
                    'platform': 'Linux',
                    'architecture': 'unknown',
                    'boot_time': 'unknown',
                    'uptime_days': 0,
                    'uptime_hours': 0,
                    'users_count': 0
                }
            }
            
            return formatted_data
            
        except Exception as e:
            print(f"SSH data collection failed for {ip}: {e}")
            return None

    def get_windows_data_via_ssh(self, host_info):
        """Haal Windows data op via SSH met PowerShell commands"""
        ip = host_info['ip']
        ssh_user = host_info.get('ssh_user', 'Administrator')
        
        try:
            # Test SSH connectivity first
            ssh_test = subprocess.run([
                'ssh', '-o', 'ConnectTimeout=5', '-o', 'StrictHostKeyChecking=no',
                f'{ssh_user}@{ip}', 'echo "connected"'
            ], capture_output=True, text=True, timeout=10)
            
            if ssh_test.returncode != 0:
                print(f"SSH connection failed to Windows {ip}: {ssh_test.stderr}")
                return None

            # Windows PowerShell commands via SSH
            commands = {
                'cpu_usage': 'powershell "Get-Counter \'\\\\Processor(_Total)\\\\% Processor Time\' -SampleInterval 1 -MaxSamples 1 2>$null | Select-Object -ExpandProperty CounterSamples | Select-Object -ExpandProperty CookedValue | ForEach-Object {[math]::Round($_, 1)}"',
                'memory_usage': 'powershell "Get-WmiObject -Class Win32_OperatingSystem | ForEach-Object {[math]::Round(($_.TotalVisibleMemorySize - $_.FreePhysicalMemory)*100/$_.TotalVisibleMemorySize,1)}"',
                'disk_usage': 'powershell "Get-WmiObject -Class Win32_LogicalDisk -Filter \\"DriveType=3\\" | ForEach-Object {[math]::Round(($_.Size - $_.FreeSpace)*100/$_.Size,1)} | Select-Object -First 1"',
                'hostname': 'hostname',
                'memory_total': 'powershell "Get-WmiObject -Class Win32_ComputerSystem | Select-Object -ExpandProperty TotalPhysicalMemory | ForEach-Object {[math]::Round($_/1MB)}"',
                'disk_total': 'powershell "Get-WmiObject -Class Win32_LogicalDisk -Filter \\"DriveType=3\\" | ForEach-Object {[math]::Round($_.Size/1GB)} | Measure-Object -Sum | Select-Object -ExpandProperty Sum"',
                'process_count': 'powershell "Get-Process | Measure-Object | Select-Object -ExpandProperty Count"'
            }
            
            data = {}
            for key, command in commands.items():
                try:
                    result = subprocess.run([
                        'ssh', '-o', 'ConnectTimeout=5', '-o', 'StrictHostKeyChecking=no',
                        f'{ssh_user}@{ip}', command
                    ], capture_output=True, text=True, timeout=15)  # Longer timeout for Windows
                    
                    if result.returncode == 0:
                        value = result.stdout.strip()
                        if key in ['cpu_usage', 'memory_usage', 'disk_usage']:
                            try:
                                clean_value = value.replace(',', '.').strip()
                                data[key] = float(clean_value)
                            except ValueError:
                                print(f"Could not parse Windows {key}: '{value}'")
                                data[key] = 0.0
                        elif key in ['process_count', 'memory_total', 'disk_total']:
                            try:
                                data[key] = int(float(value))
                            except ValueError:
                                data[key] = 0
                        else:
                            data[key] = value
                    else:
                        data[key] = None
                        print(f"Windows SSH command failed for {key}: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    print(f"Windows SSH command timeout for {key}")
                    data[key] = None
            
            # Format data in expected structure
            formatted_data = {
                'cpu': {
                    'usage_percent': data.get('cpu_usage', 0),
                    'core_count': 1,
                    'frequency_mhz': 0
                },
                'memory': {
                    'usage_percent': data.get('memory_usage', 0),
                    'total_gb': round(data.get('memory_total', 0) / 1024, 2) if data.get('memory_total') else 0,
                    'used_gb': 0,
                    'available_gb': 0
                },
                'disk': {
                    'usage_percent': data.get('disk_usage', 0),
                    'total_gb': data.get('disk_total', 0),
                    'used_gb': 0,
                    'free_gb': 0
                },
                'network': {
                    'bytes_sent_mb': 0,
                    'bytes_recv_mb': 0,
                    'packets_sent': 0,
                    'packets_recv': 0,
                    'active_connections': 0
                },
                'processes': [
                    {'pid': 0, 'name': 'powershell-data', 'cpu_percent': 0, 'memory_percent': 0}
                ],
                'system': {
                    'hostname': data.get('hostname', 'unknown'),
                    'platform': 'Windows',
                    'architecture': 'unknown',
                    'boot_time': 'unknown',
                    'uptime_days': 0,
                    'uptime_hours': 0,
                    'users_count': 0
                }
            }
            
            return formatted_data
            
        except Exception as e:
            print(f"Windows SSH data collection failed for {ip}: {e}")
            return None

    def get_basic_data(self, host_info):
        """Haal basis informatie op (ping + poorten)"""
        ip = host_info['ip']
        
        # Test connectivity
        ping_success = self.ping_host(ip)
        
        if not ping_success:
            return None
        
        # Check common ports
        services = {
            'ssh': self.check_port(ip, 22),
            'http': self.check_port(ip, 80),
            'https': self.check_port(ip, 443),
            'rdp': self.check_port(ip, 3389),  # Windows RDP
            'smb': self.check_port(ip, 445),   # Windows SMB
            'mysql': self.check_port(ip, 3306),
            'postgresql': self.check_port(ip, 5432)
        }
        
        # Create minimal data structure
        formatted_data = {
            'cpu': {
                'usage_percent': 0,  # Not available via basic check
                'core_count': 0,
                'frequency_mhz': 0
            },
            'memory': {
                'usage_percent': 0,  # Not available
                'total_gb': 0,
                'used_gb': 0,
                'available_gb': 0
            },
            'disk': {
                'usage_percent': 0,  # Not available
                'total_gb': 0,
                'used_gb': 0,
                'free_gb': 0
            },
            'network': {
                'bytes_sent_mb': 0,
                'bytes_recv_mb': 0,
                'packets_sent': 0,
                'packets_recv': 0,
                'active_connections': sum(services.values())  # Count of open ports
            },
            'processes': [
                {'pid': 0, 'name': 'basic-check', 'cpu_percent': 0, 'memory_percent': 0}
            ],
            'system': {
                'hostname': ip,  # Use IP as hostname
                'platform': host_info.get('type', 'unknown').title(),
                'architecture': 'unknown',
                'boot_time': 'unknown',
                'uptime_days': 0,
                'uptime_hours': 0,
                'users_count': 0
            },
            'services': services  # Extra info about available services
        }
        
        return formatted_data

    def get_host_data(self, host_id):
        """Haal data op van een specifieke host"""
        if not MONITORED_HOSTS.get(host_id, {}).get('enabled'):
            print(f"🔴 DEBUG: Host {host_id} is disabled, skipping...")
            return None
            
        # Voor localhost, gebruik de lokale monitor
        if self.is_localhost(host_id):
            print(f"🟡 DEBUG: Collecting data from localhost ({host_id})...")
            try:
                data = self.local_monitor.collect_current_data()
                self.hosts_status[host_id] = 'online'
                self.hosts_data[host_id] = data
                self.last_update[host_id] = datetime.now()
                print(f"✅ DEBUG: Successfully collected data from localhost ({host_id})")
                return data
            except Exception as e:
                print(f"❌ DEBUG: Error collecting local data from {host_id}: {e}")
                self.hosts_status[host_id] = 'error'
                return None
        
        # Voor remote hosts, bepaal monitoring methode
        host_info = MONITORED_HOSTS[host_id]
        monitoring_method = host_info.get('monitoring_method', 'basic')
        
        print(f"🔵 DEBUG: Attempting to connect to {host_id} ({host_info['name']}) via {monitoring_method}...")
        
        try:
            data = None
            
            if monitoring_method == 'ssh' and host_info.get('type') == 'linux':
                data = self.get_linux_data_via_ssh(host_info)
            elif monitoring_method == 'ssh' and host_info.get('type') == 'windows':
                data = self.get_windows_data_via_ssh(host_info)
            elif monitoring_method == 'wmi' and host_info.get('type') == 'windows':
                data = self.get_windows_data_via_wmi(host_info)
            else:
                # Fallback to basic monitoring
                data = self.get_basic_data(host_info)
            
            if data:
                self.hosts_status[host_id] = 'online'
                self.hosts_data[host_id] = data
                self.last_update[host_id] = datetime.now()
                print(f"✅ DEBUG: Successfully retrieved data from {host_id} ({host_info['name']})")
                return data
            else:
                print(f"❌ DEBUG: No data retrieved from {host_id} ({host_info['name']})")
                self.hosts_status[host_id] = 'offline'
                return None
                
        except Exception as e:
            print(f"❌ DEBUG: Unexpected error connecting to {host_id} ({host_info['name']}): {e}")
            self.hosts_status[host_id] = 'error'
            return None

    def update_single_host(self, host_id):
        """Update data voor een enkele host (voor threading)"""
        self.get_host_data(host_id)

    def update_all_hosts(self):
        """Update data van alle hosts (parallel)"""
        print(f"🚀 DEBUG: Starting parallel update of all hosts at {datetime.now().strftime('%H:%M:%S')}")
        
        enabled_hosts = [host_id for host_id, host_info in MONITORED_HOSTS.items() if host_info.get('enabled')]
        print(f"📊 DEBUG: Updating {len(enabled_hosts)} enabled hosts: {', '.join(enabled_hosts)}")
        
        threads = []
        
        for host_id in enabled_hosts:
            thread = threading.Thread(target=self.update_single_host, args=(host_id,))
            thread.start()
            threads.append((thread, host_id))
            print(f"🧵 DEBUG: Started thread for host {host_id}")
        
        # Wacht tot alle threads klaar zijn
        completed_threads = 0
        for thread, host_id in threads:
            thread.join(timeout=REQUEST_TIMEOUT + 2)
            completed_threads += 1
            if thread.is_alive():
                print(f"⚠️ DEBUG: Thread for {host_id} timed out after {REQUEST_TIMEOUT + 2}s")
            else:
                print(f"✅ DEBUG: Thread for {host_id} completed ({completed_threads}/{len(threads)})")
        
        print(f"🏁 DEBUG: All host updates completed at {datetime.now().strftime('%H:%M:%S')}")

    def get_all_hosts_summary(self):
        """Krijg een samenvatting van alle hosts"""
        summary = {}
        
        for host_id, host_info in MONITORED_HOSTS.items():
            if not host_info.get('enabled'):
                continue
                
            data = self.hosts_data.get(host_id)
            status = self.hosts_status.get(host_id, 'unknown')
            last_update = self.last_update.get(host_id)
            
            summary[host_id] = {
                'info': host_info,
                'status': status,
                'last_update': last_update,
                'data': data
            }
            
            # Voeg extra status informatie toe
            if data:
                summary[host_id].update({
                    'cpu_usage': data.get('cpu', {}).get('usage_percent', 0),
                    'memory_usage': data.get('memory', {}).get('usage_percent', 0),
                    'disk_usage': data.get('disk', {}).get('usage_percent', 0),
                    'active_processes': len(data.get('processes', [])),
                    'uptime_days': data.get('system', {}).get('uptime_days', 0),
                    'alerts': self.get_host_alerts(data) if data else []
                })
        
        return summary

    def get_host_alerts(self, data):
        """Krijg alerts voor een host gebaseerd op data"""
        return self.local_monitor.get_alerts(data)

    def get_overall_status(self):
        """Krijg algemene status van alle hosts"""
        total_hosts = len([h for h in MONITORED_HOSTS.values() if h.get('enabled')])
        online_hosts = len([s for s in self.hosts_status.values() if s == 'online'])
        offline_hosts = len([s for s in self.hosts_status.values() if s in ['offline', 'timeout']])
        error_hosts = len([s for s in self.hosts_status.values() if s == 'error'])
        
        return {
            'total': total_hosts,
            'online': online_hosts,
            'offline': offline_hosts,
            'errors': error_hosts,
            'health_percentage': round((online_hosts / total_hosts * 100) if total_hosts > 0 else 0, 1)
        }