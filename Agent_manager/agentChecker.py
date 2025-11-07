#verwerk hier een get request naar de agent to checken of die online + versie
import requests
from MariaDB.connector import databaseConnection 


def check_agent_status():
     databaseConnection("SELECT DATABASE();")