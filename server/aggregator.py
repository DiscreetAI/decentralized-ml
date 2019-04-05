from state import state, state_lock, reset_state
from message import Message


def handle_new_weights(serialized_message):
    # One of the clients has sent us a message.
    message = Message(serialized_message)

    # 1. If the round in the received message doesn't match the internal round,
    # then discard the message.
    if state.current_round != message.current_round:
        return {
            "error": True,
            "message": "The round in the message doesn't match the current round."
        }


    # 2 Lock section/variables that will be changed...
    state_lock.acquire()


    # 3. Do running weighted average on the new weights.
    do_running_weighted_average(message.update)


    # 4. Update the number of nodes averaged (+1)
    state.state["num_nodes_averaged"] += 1


    # 5. Log this update.
    log_update("UPDATE_RECEIVED", message)


    # 6. If 'Continuation Criteria' is met...
    if check_continuation_criteria(message.continuation_criteria):

        # 6.a. Log the resulting weights for the user (for this round)
        log_update("ROUND_COMPLETED", message)


        # 6.b. Update round number (+1)
        state.state["current_round"] += 1


        # 6.c. If 'Termination Criteria' isn't met, then kickstart a new FL round
        # NOTE: We need a way to swap the weights from the initial message
        # in node............
        if not check_termination_criteria(message.termination_criteria):
            kickstart_new_round()


    ##### NOTE: Change this to do a new round right after the last thing is averaged. It's better.


    # 7. If 'Termination Criteria' is met...
    if check_termination_criteria(message.termination_criteria):

        # 7.a. Log the resulting weights for the user (for this session)
        log_update("TRAINING_COMPLETED", message)


        # 7.b. Reset all state in the service and mark BUSY as false
        reset_state()


    # 8. Release section/variables that were changed...
    state_lock.release()

def log_update(type, message):
    """
    Connect using `state.state["logging_credentials"]`.
    """
    logging.debug
