# Multi-Host System Monitor

Een krachtige, web-gebaseerde system monitoring tool die meerdere hosts tegelijkertijd kan monitoren. Biedt real-time inzicht in CPU, geheugen, disk en netwerk gebruik van alle hosts in je infrastructuur.

## Nieuw in deze versie ✨

### Multi-Host Monitoring
- **Dashboard overview**: Bekijk alle hosts in één overzicht met status indicators
- **Individual host details**: Klik door voor gedetailleerde informatie per host
- **Automatic host discovery**: Configureer hosts in `config.py`
- **Status monitoring**: Online/Offline/Error status per host
- **Parallel data collection**: Efficiënte data verzameling van alle hosts tegelijk

### Ondersteunde Host Types
- **Windows Server** (Active Directory)
- **Linux Ubuntu** (Database/Webserver)
- **Local Host** monitoring

## Features

### 📊 Real-time Monitoring
- CPU gebruik en core informatie
- Geheugen (RAM + SWAP) statistieken  
- Disk ruimte en I/O
- Netwerk verkeer en connecties
- Top 10 processen per host
- System uptime en informatie

### 🚨 Alert System
- Configureerbare drempels voor CPU, Memory en Disk
- Visual indicators voor kritieke waarden
- Host status monitoring (online/offline/error)

### 🌐 Multi-Host Architecture
- **Central Dashboard**: Monitor alle hosts vanuit één locatie
- **Distributed Agents**: Elke host draait zijn eigen monitoring agent
- **REST API**: JSON endpoints voor integratie
- **Responsive UI**: Bootstrap-gebaseerde interface

## Quick Start

### 1. Central Monitoring Server (Main Host)
```bash
# Clone/download project
cd /path/to/monitoring

# Install dependencies
sudo apt update
sudo apt install python3-flask python3-psutil python3-requests -y

# Start monitoring server
python3 Main.py
```

### 2. Remote Host Setup (Voor elke host die je wilt monitoren)
```bash
# Copy monitoring files naar remote host
scp -r /home/ridderleeuw/Monitoring user@192.168.2.1:/opt/monitoring/

# Op de remote host:
cd /opt/monitoring
sudo apt install python3-flask python3-psutil -y

# Start monitoring agent
python3 Main.py
```

### 3. Configuration
Edit `config.py` om je hosts toe te voegen:
```python
MONITORED_HOSTS = {
    'windows-ad': {
        'name': 'Windows Server - AD',
        'ip': '192.168.2.1',
        'type': 'windows',
        'port': 5000,
        'enabled': True
    },
    # Voeg meer hosts toe...
}
```

## Host Setup Instructies

### Windows Server (192.168.2.1)
```powershell
# Install Python 3.11+
# Download monitoring code
# Install Flask: pip install flask psutil

# Open Firewall
New-NetFirewallRule -DisplayName "System Monitor" -Direction Inbound -Port 5000 -Protocol TCP -Action Allow

# Start service
python Main.py
```

### Ubuntu Database Server (192.168.2.2)
```bash
sudo apt update
sudo apt install python3-flask python3-psutil -y

# Copy monitoring files
git clone <repository> /opt/monitoring
cd /opt/monitoring

# Open firewall
sudo ufw allow 5000

# Start service
python3 Main.py
```

### Ubuntu Webserver (192.168.2.3)
```bash
# Same as database server
sudo apt install python3-flask python3-psutil -y
# Setup monitoring and start on port 5000
```

## API Endpoints

### Multi-Host Endpoints
- `GET /` - Multi-host dashboard
- `GET /api/hosts` - All hosts summary JSON
- `GET /api/host/<host_id>` - Specific host data
- `GET /host/<host_id>` - Individual host detail page

### Single-Host Endpoints (for API compatibility)
- `GET /api/data` - Single host JSON data
- `GET /api/history` - Historical data

## Configuration

### Main Settings (`config.py`)
```python
# Server Settings
HOST = '0.0.0.0'          # Listen on all interfaces
PORT = 5000               # Default port
DEBUG = True              # Enable debug mode

# Monitoring Settings
REFRESH_INTERVAL = 5      # Auto-refresh seconds
MAX_HISTORY_POINTS = 100  # History buffer size

# Alert Thresholds
CPU_WARNING_THRESHOLD = 80    # CPU warning %
MEMORY_WARNING_THRESHOLD = 80 # Memory warning %  
DISK_WARNING_THRESHOLD = 90   # Disk critical %

# Multi-Host Configuration
MONITORED_HOSTS = {
    'host-id': {
        'name': 'Display Name',
        'ip': 'IP Address',
        'type': 'windows|linux',
        'port': 5000,
        'enabled': True
    }
}
```

### Security Considerations
- Standaard draait de service op alle interfaces (`0.0.0.0`)
- Voor productie: gebruik specifieke IP's en SSL
- Configureer firewall rules per host
- Overweeg authentication voor productie omgevingen

## URLs

### Multi-Host Dashboard
- **Main Dashboard**: http://192.168.2.5:5000/
- **Windows AD**: http://192.168.2.5:5000/host/windows-ad
- **Ubuntu DB**: http://192.168.2.5:5000/host/ubuntu-db  
- **Ubuntu Web**: http://192.168.2.5:5000/host/ubuntu-web
- **Local Host**: http://192.168.2.5:5000/host/localhost

### API Access
- **All Hosts API**: http://192.168.2.5:5000/api/hosts
- **Specific Host API**: http://192.168.2.5:5000/api/host/windows-ad

## Troubleshooting

### Host Shows as Offline
1. Controleer of monitoring service draait op de host
2. Test connectiviteit: `ping <host-ip>`
3. Controleer firewall settings (poort 5000)
4. Verificeer host configuratie in `config.py`

### Performance Tips
- Verhoog `REFRESH_INTERVAL` voor meer hosts
- Disable hosts die niet nodig zijn via `enabled: False`
- Monitor netwerk verkeer bij veel hosts

### Common Issues
- **Connection timeout**: Verhoog `CONNECTION_TIMEOUT` in config
- **Slow loading**: Controleer netwerk latency tussen hosts
- **Memory usage**: Verlaag `MAX_HISTORY_POINTS` voor minder geheugen

## Development

### Project Structure
```
Monitoring/
├── Main.py                 # Flask application
├── monitor.py             # Single host monitoring
├── multi_host_monitor.py  # Multi-host management  
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── templates/
│   ├── dashboard.html     # Multi-host dashboard (main)
│   ├── host_detail.html   # Individual host view
│   └── host_offline.html  # Offline host page
└── static/
    ├── css/style.css
    └── js/charts.js
```

### Requirements
- Python 3.8+
- Flask 3.0.0
- psutil 5.9.6
- requests 2.31.0

## License
MIT License - Zie LICENSE bestand voor details.