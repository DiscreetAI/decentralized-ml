from enum import Enum


class MessageType(Enum):
    NEW_SESSION = "NEW_SESSION"
    NEW_WEIGHTS = "NEW_WEIGHTS"


class Message:
    def __init__(self, serialized_message):
        pass

    def serialize_message(self):
        pass
