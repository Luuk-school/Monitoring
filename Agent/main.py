# This is a script on its own, not part of a package.
import psutil
import requests
from agentInfo import getAgentInfo
import time



def getsysteminfo():
    test = psutil.cpu_percent(interval=1)
    print(test)

def sendAgentVersionData():
    
    data = getAgentInfo()
    api = "http://192.168.2.5:5000/api/agentInfo"
    response = requests.post(api, json=data)
    print(response.text)



#data = {"cpu": psutil.cpu_percent(interval=1),
#}
#api = "http://192.168.2.5:5000/api/data"
#response = requests.post(api, json=data)
#print(response.text)


if __name__ == "__main__":
   sendAgentVersionData() #stuurt info naar de server