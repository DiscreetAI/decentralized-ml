from enum import Enum

class MessageType(Enum):
    NEW_SESSION = "NEW_SESSION"
    NEW_WEIGHTS = "NEW_WEIGHTS"


class Message:
    @staticmethod
    def make(serialized_message):
        type, data = serialized_message["type"], serialized_message
        for cls in Message.__subclasses__():
            print(cls.type)
            if cls.type == type:
                return cls(data)
        raise ValueError("Message type is invalid!")


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
        self.hyperparams = serialized_message["hyperparams"]
