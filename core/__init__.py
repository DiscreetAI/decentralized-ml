import sys
import asyncio

import json
import base64

import websockets

class Explora(object):
    """
    Communicate with given cloud node and initiate DML session
    """
    def __init__(self):
        #log.startLogging(sys.stdout)
        self.CLOUD_BASE_URL = ".au4c4pd2ch.us-west-1.elasticbeanstalk.com"

    def start_new_session(self, repo_id, model, hyperparams, percentage_averaged, max_rounds, checkpoint_frequency=1):
        self.CLOUD_NODE_HOST = repo_id + self.CLOUD_BASE_URL

        model.save("core/model/my_model.h5")
        with open("core/model/my_model.h5", mode='rb') as file:
            file_content = file.read()
            encoded_content = base64.b64encode(file_content)
            h5_model = encoded_content.decode('ascii')

        NEW_MESSAGE = {
            "type": "NEW_SESSION",
            "repo_id": repo_id,
            "h5_model": h5_model,
            "hyperparams": hyperparams,
            "checkpoint_frequency": checkpoint_frequency,
            "selection_criteria": {
                "type": "ALL_NODES",
            },
            "continuation_criteria": {
                "type": "PERCENTAGE_AVERAGED",
                "value": percentage_averaged
            },
            "termination_criteria": {
                "type": "MAX_ROUND",
                "value": max_rounds
            }
        }

        NEW_CONNECTION_MESSAGE = {
            "type": "REGISTER",
            "node_type": "dashboard",
        }

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._start_new_session(NEW_CONNECTION_MESSAGE, NEW_MESSAGE))


    async def _start_new_session(new_connection_message, new_message):
        async with websockets.connect(self.CLOUD_NODE_HOST, max_size=2**22) as websocket:
            await websocket.send(json.dumps(new_connection_message))
            await websocket.send(json.dumps(new_message))
            response = await websocket.recv()
            json_response = json.loads(response)
            if json_response.get("action", None) == 'STOP':
                print("Session complete! Check dashboard for final model!")
            else:
                print("Unknown response received:")
                print(json_response)
                print("Stopping...")

