# verwerk hier de connectie met de  database
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()
user = os.getenv("DB_user")
password = os.getenv("DB_wachtwoord")
database = os.getenv("DB_naam")
host = os.getenv("DB_host")
debug = os.getenv("debug", "0").lower() in ("1", "true", "yes")


def databaseConnection(sql_query, parameters=None):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
        )
        print("Database connection successful")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return

    cur = connection.cursor()

    try:
        if parameters:
            cur.execute(sql_query, parameters)
        else:
            cur.execute(sql_query)
        

        if cur.with_rows:
            rows = cur.fetchall()
            if debug:
                # print up to 100 rows for debugging
                for i, row in enumerate(rows):
                    print(row)
                    if i >= 99:
                        break
        if debug:
            # show summary / all rows (may be large) and connection info
            try:
                print(f"database rows: {rows}")
            except NameError:
                print("database rows: <no rows fetched>")
            print(f"test: user={user}, password={password}, database={database}, host={host}")

        connection.commit() 
    except mysql.connector.Error as err:
        print(f"Error executing query: {err}")
    finally:
        cur.close()
        connection.close()

#if debug:
 #   databaseConnection("SELECT DATABASE();")