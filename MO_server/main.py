import flaskWebsite
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from Agent_manager.agentChecker import check_agent_status as agent_check


if agent_check(None):
    print("Agent is running")
else:
    print("Agent is not running")

    

if __name__ == "__main__":
    flaskWebsite.app.run(host='0.0.0.0')               #vraag aan bjorn hoe dit werkt en waarom het werkt??????
