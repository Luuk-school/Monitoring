# System Monitoring Dashboard

Een professionele web-gebaseerde monitoring applicatie die real-time system resources toont.

## Features

- 📊 **Real-time monitoring**: CPU, Memory, Disk, Network usage
- 🚨 **Alerting systeem**: Automatische waarschuwingen bij hoge resource usage
- 📈 **Historische data**: Grafieken met resource trends over tijd
- 🖥️ **System informatie**: OS details, uptime, running processes
- 🎨 **Moderne UI**: Responsive design met auto-refresh
- ⚡ **RESTful API**: JSON endpoints voor externe integratie

## Installatie

1. **Clone de repository:**
   ```bash
   git clone https://github.com/Luuk-school/Monitoring.git
   cd Monitoring
   ```

2. **Installeer dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

## Gebruik

**Start de applicatie:**
```bash
python3 Main.py
```

De applicatie start en is beschikbaar op:
- **Dashboard**: http://0.0.0.0:5000 (toegankelijk vanaf alle interfaces)
- **API endpoint**: http://0.0.0.0:5000/api/data
- **Historie API**: http://0.0.0.0:5000/api/history

## Configuratie

Pas de instellingen aan in `config.py`:
- `HOST`: Server host (standaard: '0.0.0.0' - alle interfaces)
- `PORT`: Server poort (standaard: 5000)
- `DEBUG`: Debug modus (standaard: False)
- `REFRESH_INTERVAL`: Auto-refresh interval in seconden
- Alert thresholds voor CPU, Memory en Disk usage

## Project Structuur

```
Monitoring/
├── Main.py              # Hoofdapplicatie (Flask server)
├── monitor.py           # System monitoring logica
├── config.py            # Configuratie instellingen
├── requirements.txt     # Python dependencies
├── templates/
│   └── index.html      # HTML template
└── static/
    └── style.css       # CSS styling
```

## API Endpoints

- `GET /` - Dashboard homepage
- `GET /api/data` - Real-time system data (JSON)
- `GET /api/history` - Historische data (JSON)

## Stoppen

Gebruik `Ctrl+C` in de terminal om de applicatie te stoppen.