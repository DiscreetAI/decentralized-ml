import logging

from state import state, state_lock, reset_state
from coordinator import start_new_session
from message import Message


logging.basicConfig(level=logging.DEBUG)

def handle_new_weights(serialized_message, clients_list):
    # 0. Decode the message.
    message = Message(serialized_message)


    # 1. Check things match.
    if state.session_id != message.session_id:
        return {
            "error": True,
            "message": "The session id in the message doesn't match the service's."
        }

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
            kickstart_new_round(clients_list)

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
    logging.debug("[{0}]: {1}".format(type, message))


def kickstart_new_round(clients_list):
    """
    Selects new nodes to run federated averaging with, and pass them the new
    averaged model.
    """
    new_serialized_message = None # Make this up again! (but update things like
                                  # weights, round, etc...)
    state.state["busy"] = False
    start_new_session(new_serialized_message, clients_list)


def do_running_weighted_average(update):
    # If this is the first weights we're averaging, just update them and return
    if not state.state["current_weights"] or not state.state["sigma_omega"]:
        state.state["current_weights"] = update["weights"]
        state.state["sigma_omega"] = update["omega"]
        return

    # Get the variables ready
    current_weights = state.state["current_weights"]
    sigma_omega = state.state["sigma_omega"]
    new_weights = update["weights"]
    new_omega = update["omega"]

    # Run the math
    temp = np.multiply(current_weights, sigma_omega)
    temp = np.add(temp, np.multiply(new_weights, new_omega))
    new_sigma_omega = np.add(sigma_omega, new_omega)
    new_weighted_avg = np.divide(temp, new_sigma_omega)

    # Update state
    print(new_weighted_avg, new_sigma_omega)
    state.state["current_weights"] = new_weighted_avg
    state.state["current_omega"] = new_sigma_omega


def check_continuation_criteria(continuation_criteria):
    """
    Right now only implements percentage of nodes averaged.
    """
    if "type" not in continuation_criteria:
        raise Exception("Continuation criteria is not well defined.")

    if continuation_criteria["type"] == "percentage_averaged":
        percentage = state.state["num_nodes_averaged"] / state.state["num_nodes_chosen"]
        return continuation_criteria["value"] >= percentage
    else:
        raise Exception("Continuation criteria is not well defined.")


def check_termination_criteria(termination_criteria):
    """
    Right now only implements a maximum amount of rounds.
    """
    if "type" not in termination_criteria:
        raise Exception("Termination criteria is not well defined.")

    if termination_criteria["type"] == "max_round":
        return termination_criteria["value"] >= state.state["current_round"]
    else:
        raise Exception("Termination criteria is not well defined.")
