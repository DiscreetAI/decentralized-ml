import time

from flask import Flask
from werkzeug.serving import run_simple

from custom.keras               import get_optimizer
from models.keras_perceptron    import KerasPerceptron
from core.utils.dmljob          import DMLJob


class FlaskTestingCommunicationManager:
    """
    Flask Testing Communication Manager

    This class is for debugging/testing purposes. It implements a communication
    manager based on Flask so that we can test the UNIX Service functionalities
    without an active P2P Network.

    """

    def __init__(self, config_manager):
        """
        Initializes the instance.
        """
        self.config_manager = config_manager

    def configure(self, scheduler):
        self.listener = FlaskListener(scheduler=scheduler)

    def start(self):
        """
        Starts the communication manager (only the listening).
        """
        if not self.listener:
            raise Exception("Communication Manager needs to be configured first.")
        self.listener.start_listening()


class FlaskListener:
    """
    Flask Listener

    This class is for debugging/testing purposes. It implements a listener based
    on Flask so that we can test the UNIX Service functionalities without an
    active P2P Network.

    """

    def __init__(self, scheduler):
        """
        Initializes the listener.
        """
        self.scheduler = scheduler
        self.app = Flask(__name__)
        self._set_up_endpoints()

    def _set_up_endpoints(self):
        """
        Sets up the endpoints of the listener.
        """
        self.app.add_url_rule('/', 'heartbeat', self.heartbeat)
        self.app.add_url_rule('/init_job_async', 'init_job_async', self.init_job_async)
        self.app.add_url_rule('/init_job_sync', 'init_job_sync', self.init_job_sync)
        self.app.add_url_rule('/scheduler', 'print_scheduler', self.print_scheduler)

    def start_listening(self):
        """
        Starts listening on a port.
        """
        run_simple(
            'localhost',
            5000,
            self.app,
            processes=1,
            use_reloader=False,
            use_debugger=False,
            use_evalex=False
        )

    def heartbeat(self):
        """
        Prints something indicating the listener is up and running.
        """
        return "I'm working!"

    def init_job_sync(self):
        """
        Initialize a model (sync).
        """
        initialize_job = make_initialize_job(make_model_json())
        self.scheduler.add_job(initialize_job)
        while not self.scheduler.processed:
            time.sleep(3)
        initial_weights = self.scheduler.processed.pop(0)
        return str(initial_weights)

    def init_job_async(self):
        """
        Initialize a model (async).
        """
        initialize_job = make_initialize_job(make_model_json())
        self.scheduler.add_job(initialize_job)
        return "done"

    def print_scheduler(self):
        """
        Check scheduler status.
        """
        output = ""
        for i, runner in enumerate(self.scheduler.runners):
            output += "Runner {}: (current job: {})".format(
                str(i + 1),
                "running" if self.scheduler.current_jobs[i] else "none"
            )
            output += "<br>"

        output += "<br>History Output:<br>"
        for i, processed_item in enumerate(self.scheduler.history):
            output += str(i + 1) + " - " + str(processed_item)[:100] + "<br>"
        return output


def make_model_json():
    """
    Helper function to make the JSON representation of a Perceptron model.
    """
    m = KerasPerceptron(is_training=True)
    model_architecture = m.model.to_json()
    model_optimizer = get_optimizer(m.model)
    model_json = {
        "architecture": model_architecture,
        "optimizer": model_optimizer
    }
    return model_json


def make_initialize_job(model_json):
    """
    Helper function to make an DMLJob of 'initialize' type.
    """
    initialize_job = DMLJob(
        "initialize",
        model_json,
        "keras"
    )
    return initialize_job
