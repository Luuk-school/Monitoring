# verwerk hier de connectie met de  database
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()
user = os.getenv("DB_user")
password = os.getenv("DB_wachtwoord")
database = os.getenv("DB_naam")
host = os.getenv("DB_host")


def createConnection():
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=datbase
    )
    return connection

#verwijder deze print statement later weer
print(f"test: user={user}, password={password}, database={database}, host={host}")
