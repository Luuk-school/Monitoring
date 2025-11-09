# Monitoring script gemaakt voor school.
Monitoring script gemaakt voor school.
De monitoring werkt via http-methods om data optevragen van een agent.
data wordt opgeslagen in een database en weer uitgelezen om te verwerken op een website.


Installatie en gebruik
---------------------

Download de `Agent` folder en start de agent op de target-machine met de volgende stappen:

1. Update en installeer benodigde pakketten:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip subversion -y
```

2. Haal de `Agent` folder op vanuit GitHub:

```bash
svn export https://github.com/Luuk-school/Monitoring/trunk/Agent
```

3. Installeer Python-vereisten (psutil en requests):

```bash
sudo apt install python3-psutil python3-requests -y
# of gebruik pip3 indien gewenst:
# pip3 install psutil requests
```

4. Start de agent:

```bash
python3 ~/Agent/main.py
```

Eén-lijns commando (copy/paste) — optie om alles in één keer te doen:

```bash
sudo apt update && sudo apt upgrade -y && sudo apt install python3 python3-pip subversion -y && svn export https://github.com/Luuk-school/Monitoring/trunk/Agent && sudo apt install python3-psutil python3-requests -y && python3 ~/Agent/main.py
```

Opmerkingen
----------
- Zorg dat de database-instellingen (in `MariaDB/connector.py`) correct zijn geconfigureerd via je environment variables.
- De server draait in `MO_server` en exposeert de webinterface op poort 5000 (standaard Flask poort).

Veel succes! Als je wilt kan ik het README nog verder uitbreiden met voorbeelden en screenshots van de webinterface.
