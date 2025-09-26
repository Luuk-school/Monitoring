# System Monitoring Configuratie

# Server instellingen
HOST = '0.0.0.0'
PORT = 5000
DEBUG = True

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
        'monitoring_method': 'ssh',  # Nu ook SSH voor Windows!
        'ssh_user': 'luuk',  # SSH gebruiker voor Windows
        'description': 'Windows Server with SSH monitoring'
    },
    'ubuntu-db': {
        'name': 'Database Server',
        'ip': '192.168.2.2', 
        'type': 'linux',
        'port': 5000,
        'enabled': True,
        'monitoring_method': 'ssh',  # SSH voor gedetailleerde info
        'ssh_user': 'ridderleeuw',  # Super user voor Linux servers
        'description': 'Linux database server with SSH monitoring'
    },
    'ubuntu-web': {
        'name': 'Webserver',
        'ip': '192.168.2.3',
        'type': 'linux', 
        'port': 5000,
        'enabled': True,
        'monitoring_method': 'ssh',  # SSH voor gedetailleerde info
        'ssh_user': 'ridderleeuw',  # Super user voor Linux servers
        'description': 'Linux webserver with SSH monitoring'
    },
    'localhost': {
        'name': 'Monitoring Server',
        'ip': '192.168.2.5',
        'type': 'linux',
        'port': 5000,
        'enabled': True,
        'monitoring_method': 'local',  # Direct psutil calls
        'description': 'Local monitoring server'
    }
}

# Connection timeout settings
CONNECTION_TIMEOUT = 5  # seconden
REQUEST_TIMEOUT = 10  # seconden