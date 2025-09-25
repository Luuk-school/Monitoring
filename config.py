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