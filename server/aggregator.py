from state import state, state_lock
from message import Message


def handle_new_weights(serialized_message):
    # // One of the clients has sent us a message.
    message = Message(serialized_message)

    # // 1. If the round in the received message doesn't match the internal round,
    # //    then discard the message.
    if state.current_round != message.current_round:
        return {
            "error": True,
            "message": "The round in the message doesn't match the current round."
        }

    # // 2 Lock section/variables that will be changed...
    state_lock.acquire()

    # // 2. If 'Continuation Criteria' isn't met...
    if not check_continuation_criteria(message.continuation_criteria):
    #     // 2.a. Do running weighted average on the new weights.
    #     // 2.b. Update the number of nodes averaged (+1)
        do_running_weighted_average(message.update)

    # // 3. If 'Continuation Criteria' is met...
    else:

    #     // 3.a. Update the number of nodes averaged (+1)
        state.state["num_nodes_averaged"] += 1

    #     // 3.b. Log the resulting weights for the user (for this round)
        log_update(message)

    #     // 3.c. Update round number (+1)
        state.state["current_round"] += 1

    #     // 3.d. If 'Termination Criteria' isn't met, then kickstart a new FL round
    #     //      NOTE: We need a way to swap the weights from the initial message
    #     //      in node............
        if not check_termination_criteria(message.termination_criteria):
            kickstart_new_round()

    ##### NOTE: Change this to do a new round right after the last thing is averaged. It's better.


    # // 4. If 'Termination Criteria' is met...
    #
    #     // 4.a. Log the resulting weights for the user (for this session)
    #
    #     // 4.b. Reset all state in the service and mark BUSY as false
    #
    # // 5. Release section/variables that were changed...


def log_update(message):
    """
    Connect using `state.state["logging_credentials"]`.
    """
    pass
