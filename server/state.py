def init():
    import threading
    global state_lock
    state_lock = threading.Lock()

    global reset_state
    def reset_state():
        global state
        state = {
            "busy": False,
            "session_id": None,
            "current_round": 0,
            "num_nodes_averaged": 0,
            "num_nodes_chosen": 0,
            "current_weights" : None,
            "sigma_omega": None,
            "logging_credentials": {
                "host": "",
                "port": "",
                "username": "",
                "password": "",
            },
            "initial_message": None,
        }

    reset_state()
