import json
import base64

from autobahn.twisted.websocket import WebSocketClientProtocol

with open('assets/saved_mlp_model_with_w.h5', mode='rb') as file:
    file_content = file.read()
    encoded_content = base64.encodebytes(file_content)
    h5_model = encoded_content.decode('ascii')

NEW_MESSAGE = {
    "type": "NEW_SESSION",
    "h5_model": h5_model,
    "hyperparams": {
        "batch_size": 128,
        "epochs": 10,
    },
    "selection_criteria": {
        "type": "ALL_NODES",
    },
    "continuation_criteria": {
        "type": "PERCENTAGE_AVERAGED",
        "value": 0.5
    },
    "termination_criteria": {
        "type": "MAX_ROUND",
        "value": 5
    }
}

class NewSessionTestProtocol(WebSocketClientProtocol):

   def onOpen(self):
      json_data = json.dumps(NEW_MESSAGE)
      self.sendMessage(json_data.encode())

   def onMessage(self, payload, isBinary):
      if isBinary:
         print("Binary message received: {0} bytes".format(len(payload)))
      else:
         print("Text message received: {0}".format(payload.decode('utf8')))

if __name__ == '__main__':

   import sys

   from twisted.python import log
   from twisted.internet import reactor
   log.startLogging(sys.stdout)

   from autobahn.twisted.websocket import WebSocketClientFactory
   factory = WebSocketClientFactory()
   factory.protocol = NewSessionTestProtocol

   reactor.connectTCP("127.0.0.1", 8999, factory)
   reactor.run()
