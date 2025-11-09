# This is a script on its own, not part of a package.
import requests
from agentInfo import getAgentInfo
from agent import getSystemInfo
import time


test = False  #verander naar False om continue te runnen


def sendAgentVersionData():

    agent_VersionData_Data = getAgentInfo()
    api = "http://192.168.2.5:5000/api/agentInfo"
    response = requests.post(api, json=agent_VersionData_Data)
    print(response.text)

def sendSystemData():
    system_data = getSystemInfo()
    api = "http://192.168.2.5:5000/api/sysdata"
    response = requests.post(api, json=system_data)
    print(response.text)




if __name__ == "__main__":
    while True:
        time.sleep(5) #wacht 5 seconden
        sendAgentVersionData()
        sendSystemData()
        if test:
            break