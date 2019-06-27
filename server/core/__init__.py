import sys

from twisted.python import log
from twisted.internet import reactor
import json
import base64

from autobahn.twisted.websocket import WebSocketClientProtocol
from autobahn.twisted.websocket import WebSocketClientFactory

class Explora(object):

    def __init__(self):
        #log.startLogging(sys.stdout)
        self.CLOUD_BASE_URL = ".au4c4pd2ch.us-west-1.elasticbeanstalk.com"
        self.CLOUD_NODE_PORT = 80
        self.factory = WebSocketClientFactory()

    def start_new_session(self, repo_id, model, hyperparams, percentage_averaged, max_rounds):
        self.CLOUD_NODE_HOST = repo_id + self.CLOUD_BASE_URL

        model.save("../../core/model/my_model.h5")
        with open("../../core/model/my_model.h5", mode='rb') as file:
            file_content = file.read()
            encoded_content = base64.b64encode(file_content)
            h5_model = encoded_content.decode('ascii')

        NEW_MESSAGE = {
            "type": "NEW_SESSION",
            "repo_id": repo_id,
            "h5_model": h5_model,
            "hyperparams": hyperparams,
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

        class NewSessionTestProtocol(WebSocketClientProtocol):
            def onOpen(self):
                json_data = json.dumps(NEW_CONNECTION_MESSAGE)
                self.sendMessage(json_data.encode())
                json_data = json.dumps(NEW_MESSAGE)
                self.sendMessage(json_data.encode())

            def onMessage(self, payload, isBinary):
                if isBinary:
                    print("Binary message received: {0} bytes".format(len(payload)))
                else:
                    print("Text message received: {0}".format(payload.decode('utf8')))

        self.factory.protocol = NewSessionTestProtocol
        reactor.connectTCP(self.CLOUD_NODE_HOST, self.CLOUD_NODE_PORT, self.factory)
        reactor.run()
