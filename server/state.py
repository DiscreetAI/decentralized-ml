def init():
    import threading

    global state
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

    state_lock = threading.Lock()
