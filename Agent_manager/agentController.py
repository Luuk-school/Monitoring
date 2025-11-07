#agent checker
from connector import createConnection

if createConnection():
    print("Database connection successful")
else:
    print("Database connection failed")

# def check_agent_status(agent):
#    agent = 