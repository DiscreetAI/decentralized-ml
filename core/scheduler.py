import logging
import time
import json
from collections import deque
from core.utils.dmljob import DMLJob
from core.runner import DMLRunner
from threading import Event, Timer
from multiprocessing import Pool


logging.basicConfig(level=logging.DEBUG,
                    format='[Scheduler] %(asctime)s %(levelname)s %(message)s')

class DMLScheduler(object):
    """
    DML Scheduler
    This class schedules and manages the execution of DMLJobs using the DMLRunner.
    Note: now supports a multithreaded environment using multiprocessing.
    Note2: only supports one dataset type.
    Note3: Singleton.
    """
    # Here will be the instance stored.
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if DMLScheduler.__instance == None:
            DMLScheduler()
        return DMLScheduler.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if DMLScheduler.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            DMLScheduler.__instance = self
        logging.info("Setting up scheduler...")
        self.queue = deque()
        self.processed = []
        with open('core/config.json') as f:
            config = json.load(f)
            self.dataset_path = config["dataset_path"]
            self.runner_config = config["runner_config"]
            scheduler_config = config["scheduler_config"]
            self.frequency_in_mins = scheduler_config["frequency_in_mins"]
            self.num_runners = scheduler_config["num_processes"]
        self.pool = Pool(processes=self.num_runners)
        self.runners = [self.create_runner() for _ in range(self.num_runners)]
        self.current_jobs = [None]*self.num_runners
        self.results = [None]*self.num_runners
        self.event = Event()
        logging.info("Scheduler is set up!")

    def add_job(self, dml_job):
        """ Add a job to the queue"""
        assert type(dml_job) is DMLJob, "Job is not of type DMLJob."
        logging.info("Scheduling job...")
        self.queue.append(dml_job)

    def create_runner(self):
        """ Creates new runner. """
        return DMLRunner(self.dataset_path, self.runner_config)

    def _runners_run_next_jobs(self):
        """ Check each job to see if it has a job running. If not, have the runner run the
        next job on the queue asynchronously of the others and collect the result of the job
        that was running before (if applicable)
        """
        for i in range(self.num_runners):
            runner = self.runners[i]
            if not runner.is_active():
                if self.current_jobs[i]:
                    self.processed.append(self.current_jobs[i].get())
                    self.current_jobs[i] = None
                if self.queue:
                    self.current_jobs[i] = self.pool.apply_async(runner.run_job, (self.queue.popleft(),))

    def _runners_run_next_jobs_as_event(self, period):
        """ Trigger above method every period"""
        self._runners_run_next_jobs()
        if not self.event.is_set():
            Timer(period*60, self._runners_run_next_jobs_as_event, [period]).start()

    def _start_cron(self, period=None):
        """ CRON job to run next jobs on runners, if applicable. Runs asynchronously."""
        if not period:
            period = self.frequency_in_mins
        logging.info("Starting cron...")
        self._runners_run_next_jobs_as_event(period)
        logging.info("Cron started!")


    def reset(self):
        """ Scheduler is a singleton, so need to get a new instance inplace """
        logging.info("Resetting scheduler...")
        self.queue = deque()
        self.processed = []
        self.event = Event()
        logging.info("Scheduler resetted!")

    def _stop_cron(self):
        """ Tell the scheduler to stop scheduling jobs """
        logging.info("Stopping cron...")
        self.event.set()
        logging.info("Cron stopped!")


if __name__ == '__main__':
    # Set up model
    from models.keras_perceptron import KerasPerceptron
    from custom.keras import get_optimizer
    m = KerasPerceptron(is_training=True)
    model_architecture = m.model.to_json()
    model_optimizer = get_optimizer(m.model)
    model_json = {
        "architecture": model_architecture,
        "optimizer": model_optimizer
    }
    print(model_json)

    # Set up hyperparams
    from examples.labelers import mnist_labeler
    config = {}
    hyperparams = {
        'averaging_type': 'data_size',
        'batch_size': 50,
        'epochs': 1,
        'split': 0.8,
    }

    # Schedule some jobs
    from core.utils.dmljob import DMLJob

    scheduler = DMLScheduler.getInstance()

    initialize_job = DMLJob(
        "initialize",
        model_json,
        "keras"
    )
    initial_weights = scheduler.add_job(initialize_job)

    train_job = DMLJob(
        "train",
        model_json,
        "keras",
        config,
        initial_weights,
        hyperparams,
        mnist_labeler
    )
    new_weights, _, _ = scheduler.add_job(train_job)

    validate_job = DMLJob(
        "validate",
        model_json,
        'keras',
        config,
        new_weights,
        hyperparams,
        mnist_labeler
    )
    scheduler.add_job(validate_job)
