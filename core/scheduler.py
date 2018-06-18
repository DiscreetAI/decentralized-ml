# Add the parent directory to the PATH to allow imports.
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
# from multiprocessing import Pool as ThreadPool
# from multiprocessing import Process
from collections import deque
import logging
import time
import json

import schedule

from core.utils.dmljob import DMLJob
from core.runner import DMLRunner


logging.basicConfig(level=logging.DEBUG,
                    format='[Scheduler] %(asctime)s %(levelname)s %(message)s')

class DMLScheduler(object):
    """
    DML Scheduler

    This class schedules and manages the execution of DMLJobs using the DMLRunner.
    Note: currently runs in a single-threaded environment.
    Note2: only supports one dataset type.

    """

    def __init__(self):
        logging.info("Setting up scheduler...")
        self.queue = deque()
        with open('core/config.json') as f:
            config = json.load(f)
            dataset_path = config["dataset_path"]
            runner_config = config["runner_config"]
            scheduler_config = config["scheduler_config"]
            run_frequency_mins = scheduler_config["frequency_in_mins"]
            num_processes = scheduler_config["num_processes"]
        self.current_runner = DMLRunner(dataset_path, runner_config)
        #self.threading_pool = ThreadPool(num_processes)
        self._start_cron(run_frequency_mins)
        logging.info("Scheduler is set up!")

    def add_job(self, dml_job):
        assert type(dml_job) is DMLJob, "Job is not of type DMLJob."
        logging.info("Scheduling job...")
        self.queue.append(dml_job)
        return self._run_next_job_if_necessary()

    def _run_next_job_if_necessary(self):
        if not self.current_runner.is_active() and self.queue:
            # self.threading_pool.apply_async(self._run_next_job).get()
            # Process(target=self._run_next_job).start()
            return self._run_next_job()

    def _run_next_job(self):
        logging.info("Running next job...")
        current_job = self.queue.popleft()
        return_obj = self.current_runner.run_job(current_job)
        logging.info("Job complete!")
        return return_obj

    def _start_cron(self, run_frequency_mins):
        logging.info("Starting cron...")
        schedule.every(run_frequency_mins).minutes.do(self._run_next_job_if_necessary)
        schedule.run_pending()
        logging.info("Cron started!")

    # def __getstate__(self):
    #     self_dict = self.__dict__.copy()
    #     del self_dict['threading_pool']
    #     return self_dict
    #
    # def __setstate__(self, state):
    #     self.__dict__.update(state)

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

    scheduler = DMLScheduler()

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
