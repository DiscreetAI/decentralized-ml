import sys
import uuid
import json
import logging

from twisted.python import log
from twisted.web.server import Site
from twisted.internet import reactor
from twisted.web.wsgi import WSGIResource
from flask import Flask, send_from_directory
from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.twisted.websocket import WebSocketServerFactory
from autobahn.twisted.resource import WebSocketResource, WSGIRootResource

import state
from message import MessageType, Message
from coordinator import start_new_session
from aggregator import handle_new_weights


logging.basicConfig(level=logging.DEBUG)

class CloudNodeProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {}".format(request.peer))
        print(state.state)

    def onOpen(self):
        print("WebSocket connection open.")
        self.factory.register(self)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {}".format(reason))
        self.factory.unregister(self)

    def onMessage(self, payload, isBinary):
        if isBinary:
            logging.error("Binary message not supported.")
            return

        # Convert message to JSON
        try:
            serialized_message = json.loads(payload)
        except Exception:
            logging.error("Error converting JSON.")
            return

        logging.debug("Message received: {} {} {} {}".format(
            serialized_message["type"],
            serialized_message["hyperparams"],
            serialized_message["selection_criteria"],
            serialized_message["continuation_criteria"],
            serialized_message["termination_criteria"],
            serialized_message["h5_model"][:20],
        ))

        # Deserialize message
        try:
            message = Message.make(serialized_message)
        except Exception as e:
            logging.error("Error deserializing message!")
            error_json = json.dumps({"error": True, "message": "Error deserializing message: {}".format(e)})
            self.sendMessage(error_json.encode(), isBinary)
            return

        # Process message
        if message.type == MessageType.NEW_SESSION.value:
            logging.debug("New 'new session' message!")

            # Start new DML Session
            results = start_new_session(message, self.factory.clients)

            # Error check
            if results["error"]:
                self.sendMessage(json.dumps(results).encode(), isBinary)
                return

            # Handle results
            if results["action"] == "BROADCAST":
                for c in results["client_list"]:
                    results_json = json.dumps(results["message"])
                    c.sendMessage(results_json.encode(), isBinary)

        elif message.type == MessageType.NEW_WEIGHTS.value:
            logging.debug("New 'new weights' message!")

            # Handle new weights (average, move to next round, terminate session)
            results = handle_new_weights(message, self.factory.clients)

            # Error check
            if results["error"]:
                self.sendMessage(json.dumps(results).encode(), isBinary)
                return

            # Acknowledge message (temporarily! -- node doesn't need to know)
            self.sendMessage(json.dumps({"error": False}).encode(), isBinary)
        else:
            logging.error("Unknown message type!")
            error_json = json.dumps({"error": True, "message": "Unknown message type!"})
            self.sendMessage(error_json.encode(), isBinary)



class CloudNodeFactory(WebSocketServerFactory):

    def __init__(self):
        WebSocketServerFactory.__init__(self)
        self.clients = []

    def register(self, client):
        if client not in self.clients:
            print("registered client {}".format(client.peer))
            self.clients.append(client)

    def unregister(self, client):
        if client in self.clients:
            print("unregistered client {}".format(client.peer))
            self.clients.remove(client)

# // NOTE: We need to implement some ping-pong/ways to deal with disconnections.

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())

@app.route('/model/<path:filename>')
def serve_model(filename):
    """
    Serves the models to the user.

    TODO: Should do this through ngnix for a boost in performance. Should also
    have some auth token -> session id mapping (security fix in the future).
    """
    session_id = state.state["session_id"]
    round = state.state["current_round"]
    return send_from_directory(
        app.root_path + '/temp/' + session_id + "/" + str(round),
        filename,
    )


if __name__ == '__main__':

   log.startLogging(sys.stdout)

   factory = CloudNodeFactory()
   factory.protocol = CloudNodeProtocol
   wsResource = WebSocketResource(factory)

   wsgiResource = WSGIResource(reactor, reactor.getThreadPool(), app)
   rootResource = WSGIRootResource(wsgiResource, {b'': wsResource})
   site = Site(rootResource)

   state.init()

   reactor.listenTCP(8999, site)
   reactor.run()
