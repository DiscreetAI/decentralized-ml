"""This file contains all the different event types used betweent the
Communication Manager and the Optimizers."""

from enum import Enum


class MessageEventTypes(Enum):
    """
    Dictionary of events that the Blockchain Gateway might receive from the 
    Communication Manager.

    The event indicates what the Communication Manager wants the Gateway to
    do with the information it is asking it to communicate.
    """
    NEW_WEIGHTS = "NEW_WEIGHTS"
    NOTHING = "NOTHING"

class RawEventTypes(Enum):
    """
    Dictionary of events that the Optimizer might receive from the Communication
    Manager.

    The event indicates what has occurred previously in the Communication Manager.

    This is essentially a 'memory' for the Optimizer so these are all past.
    i.e., a "TRAIN" event would contain auxiliary information about what
    occurred, in the form of a DMLResults object.

    Contains all the functionality of what the Communication Manager might have
    previously done and therefore is not specific to any one Optimizer.
    """
    NEW_SESSION = "NEW_SESSION"
    NEW_WEIGHTS = "NEW_WEIGHTS"
    TERMINATE = "TERMINATE"
    JOB_FINISHED = "JOB_FINISHED"
    NOTHING = "NOTHING"

class ActionableEventTypes(Enum):
    """
    Dictionary of events that the Communication Manager might receive from the
    Optimizer.

    The event indicates what state the Optimizer has transitioned to. This is
    essentially a 'command' for the Comm. Mgr. so these are all imperatives.

    This dictionary has to contain all possible states that an Optimizer can be in.
    """
    SPLIT = "SPLIT"
    TRAIN = "TRAIN"
    AVERAGE = "AVERAGE"
    COMMUNICATE = "COMMUNICATE"
    TERMINATE = "TERMINATE"
    NOTHING = "NOTHING"

def callback_handler(
    callback_type,
    callback_dict,
    default=RawEventTypes.NOTHING.value
    ):
    """
    Helper function which returns a callback from a callback
    dict when given a callback type.
    """
    assert isinstance(callback_dict, dict), \
        "callback_dict was not a dict, it was: {}".format(type(callback_dict))
    callback = callback_dict[default]
    if callback_type in callback_dict:
        callback = callback_dict[callback_type]
    return callback