# Monitoring script gemaakt voor school.
Monitoring script gemaakt voor school.
De monitoring werkt via http-methods om data optevragen van een agent.
data wordt opgeslagen in een database en weer uitgelezen om te verwerken op een website.


donwload de agent folder:
1* sudo apt update && sudo apt upgrade -y
2* sudo apt python3 -y
2* sudo apt install subversion -y 
3* svn export https://github.com/Luuk-school/Monitoring/trunk/Agent
4* sudo apt install python3-psutil python3-requests -y
5* python3 ~/Agent/main.py

copy paste

sudo apt update && sudo apt upgrade -y && sudo apt install python3 python3-pip -y && sudo apt install subversion -y && svn export https://github.com/Luuk-school/Monitoring/trunk/Agent && sudo apt install python3-psutil python3-requests -y && python3 ~/Agent/main.py
