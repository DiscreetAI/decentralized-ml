def init():
    global state
    state = {}

    import threading
    global state_lock
    state_lock = threading.Lock()

    global reset_state
    def reset_state():
        state = {
            "busy": False,
            "current_round": 0,
            "num_nodes_averaged": 0,
            "current_weights" : None,
            "logging_credentials": {
                "host": "",
                "port": "",
                "username": "",
                "password": "",
            },
        }
    reset_state()
