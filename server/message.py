import json
import base64
from enum import Enum

import numpy as np

class MessageType(Enum):
    REGISTER = "REGISTER"
    NEW_SESSION = "NEW_SESSION"
    NEW_WEIGHTS = "NEW_WEIGHTS"


class Message:

    @staticmethod
    def make(serialized_message):
        type, data = serialized_message["type"], serialized_message
        for cls in Message.__subclasses__():
            if cls.type == type:
                return cls(data)
        raise ValueError("Message type is invalid!")


class RegistrationMessage(Message):
    """
    Registration Message

    The type of message sent by a node with information of what type of node
    they are

    """

    type = MessageType.REGISTER.value

    def __init__(self, serialized_message):
        self.node_type = serialized_message["node_type"].upper()

    def __repr__(self):
        return json.dumps({
            "node_type": self.node_type
        })


class NewSessionMessage(Message):
    """
    New Session Message

    The type of message sent by explora.

    """

    type = MessageType.NEW_SESSION.value

    def __init__(self, serialized_message):
        self.h5_model = serialized_message["h5_model"]
        self.hyperparams = serialized_message["hyperparams"]
        self.selection_criteria = serialized_message["selection_criteria"]
        self.continuation_criteria = serialized_message["continuation_criteria"]
        self.termination_criteria = serialized_message["termination_criteria"]

    def __repr__(self):
        return json.dumps({
            "h5_model": self.h5_model[:20],
            "hyperparams": self.hyperparams,
            "selection_criteria": self.selection_criteria,
            "continuation_criteria": self.continuation_criteria,
            "termination_criteria": self.termination_criteria,
        })


class NewWeightsMessage(Message):
    """
    New Weights Message

    The type of message sent by the library.

    """

    type = MessageType.NEW_WEIGHTS.value

    def __init__(self, serialized_message):
        self.session_id = serialized_message["session_id"]
        self.round = serialized_message["round"]
        self.action = serialized_message["action"]
        self.weights = np.array(
            serialized_message["results"]["weights"],
            dtype=np.dtype(float),
        )
        print("[DEBUG] size of weights {0}".format(self.weights.shape))
        print("[DEBUG] inspect {}".format(self.weights[:10]))
        self.omega = serialized_message["results"]["omega"]

    def __repr__(self):
        return json.dumps({
            "session_id": self.session_id,
            "round": self.round,
            "action": self.action,
            "weights": "omitted",
            "omega": self.omega,
        })
