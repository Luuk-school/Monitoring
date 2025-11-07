#verwerk hier informatie over de agent en stuur die naar /api/agentInfo
import socket
import json

with open('info.json', 'r') as jsonFile:
    agentData = json.load(jsonFile)

def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def getAgentInfo():
    agentData['ComputerName'] = socket.gethostname()
    agentData['IP'] = getIP()
    print(agentData)

    with open('info.json', 'w') as jsonFile:
        json.dump(agentData, jsonFile)
    return agentData
