# verwerk hier de connectie met de  database
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()
user = os.getenv("DB_user")
password = os.getenv("DB_wachtwoord")


def createConnection():
    connection = mysql.connector.connect(
        host="192.168.2.2",
        user=user,
        password=password,
        database=database
    )
    return connection

#verwijder deze print statement later weer
print(f"test: user={user}, password={password}") 
