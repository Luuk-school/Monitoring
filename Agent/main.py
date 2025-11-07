# This is a script on its own, not part of a package.
import psutil
import requests

def get_system_info():
    test = psutil.cpu_percent(interval=1)
    print(test)

get_system_info()

data = {"cpu": psutil.cpu_percent(interval=1),
}
api = "http://192.168.2.5:5000/api/data"
response = requests.post(api, json=data)
print(response.text)