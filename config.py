# System Monitoring Configuratie

# Server instellingen
HOST = '0.0.0.0'
PORT = 5000
DEBUG = False

# Monitoring instellingen
REFRESH_INTERVAL = 5  # seconden
MAX_HISTORY_POINTS = 100

# Resource thresholds (waarschuwingslimieten)
CPU_WARNING_THRESHOLD = 80  # percentage
MEMORY_WARNING_THRESHOLD = 80  # percentage  
DISK_WARNING_THRESHOLD = 90  # percentage

# Multi-host monitoring configuratie
MONITORED_HOSTS = {
    'windows-ad': {
        'name': 'Windows Server - AD',
        'ip': '192.168.2.1',
        'type': 'windows',
        'port': 5000,
        'enabled': True,
        'monitoring_method': 'ssh', 
        'ssh_user': 'luuk', 
        'description': 'Windows Server with SSH monitoring'
    },
    'ubuntu-db': {
        'name': 'Database Server',
        'ip': '192.168.2.2', 
        'type': 'linux',
        'port': 5000,
        'enabled': True,
        'monitoring_method': 'ssh',  
        'ssh_user': 'ridderleeuw', 
        'description': 'Linux database server with SSH monitoring'
    },
    'ubuntu-web': {
        'name': 'Webserver',
        'ip': '192.168.2.3',
        'type': 'linux', 
        'port': 5000,
        'enabled': True,
        'monitoring_method': 'ssh',
        'ssh_user': 'ridderleeuw', 
        'description': 'Linux webserver with SSH monitoring'
    },
    'localhost': {
        'name': 'Monitoring Server',
        'ip': '192.168.2.5',
        'type': 'linux',
        'port': 5000,
        'enabled': True,
        'monitoring_method': 'local',
        'description': 'Local monitoring server'
    }
}

# Connection timeout settings     (time in seconds)
CONNECTION_TIMEOUT = 5 
REQUEST_TIMEOUT = 10 