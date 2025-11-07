import MO_server.flaskWebsite
import sys
import os

from Agent_manager.agentChecker import check_agent_status as agent_check


if agent_check(None):
    print("Agent is running")
else:
    print("Agent is not running")

    

if __name__ == "__main__":
    MO_server.flaskWebsite.app.run(host='0.0.0.0')