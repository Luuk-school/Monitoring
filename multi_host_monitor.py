import requests
import threading
import time
from datetime import datetime
from config import MONITORED_HOSTS, CONNECTION_TIMEOUT, REQUEST_TIMEOUT
from monitor import SystemMonitor

class MultiHostMonitor:
    def __init__(self):
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
        
        # Voor remote hosts, probeer API call
        host_info = MONITORED_HOSTS[host_id]
        url = f"http://{host_info['ip']}:{host_info['port']}/api/data"
        
        print(f"🔵 DEBUG: Attempting to connect to {host_id} ({host_info['name']}) at {url}...")
        
        try:
            start_time = time.time()
            response = requests.get(
                url, 
                timeout=(CONNECTION_TIMEOUT, REQUEST_TIMEOUT),
                headers={'Accept': 'application/json'}
            )
            
            connection_time = round((time.time() - start_time) * 1000, 2)
            print(f"🔵 DEBUG: Connection to {host_id} took {connection_time}ms, status code: {response.status_code}")
            
            if response.status_code == 200:
                json_data = response.json()
                if json_data.get('success'):
                    self.hosts_status[host_id] = 'online'
                    self.hosts_data[host_id] = json_data.get('data')
                    self.last_update[host_id] = datetime.now()
                    print(f"✅ DEBUG: Successfully retrieved data from {host_id} ({host_info['name']})")
                    return json_data.get('data')
                else:
                    print(f"❌ DEBUG: API call to {host_id} returned success=false")
                    self.hosts_status[host_id] = 'error'
                    return None
            else:
                print(f"❌ DEBUG: HTTP error {response.status_code} from {host_id} ({host_info['name']})")
                self.hosts_status[host_id] = 'offline'
                return None
                
        except requests.exceptions.ConnectTimeout:
            print(f"⏰ DEBUG: Connection timeout to {host_id} ({host_info['name']}) after {CONNECTION_TIMEOUT}s")
            self.hosts_status[host_id] = 'timeout'
            return None
        except requests.exceptions.ConnectionError as e:
            print(f"🔗 DEBUG: Connection error to {host_id} ({host_info['name']}): {str(e)[:100]}...")
            self.hosts_status[host_id] = 'offline'
            return None
        except requests.exceptions.Timeout:
            print(f"⏰ DEBUG: Request timeout to {host_id} ({host_info['name']}) after {REQUEST_TIMEOUT}s")
            self.hosts_status[host_id] = 'timeout'
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
        
        # Print status summary
        status_summary = {}
        for host_id in enabled_hosts:
            status = self.hosts_status.get(host_id, 'unknown')
            status_summary[status] = status_summary.get(status, 0) + 1
        
        print(f"📈 DEBUG: Status summary: {dict(status_summary)}")
    
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