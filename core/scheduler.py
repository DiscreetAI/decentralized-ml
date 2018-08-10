import logging
import time
import json
from collections import deque
from threading import Event, Timer
from multiprocessing import Pool

from core.utils.dmljob import DMLJob
from core.runner import DMLRunner
from core.configuration import ConfigurationManager


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
    def get_instance():
        """ Static access method. """
        if DMLScheduler.__instance == None:
            DMLScheduler()
        return DMLScheduler.__instance

    def __init__(self, config_manager):
        """ Virtually private constructor. """
        if DMLScheduler.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            DMLScheduler.__instance = self
        logging.info("Setting up scheduler...")
        self.queue = deque()
        self.processed = []
        config = config_manager.get_config()
        self.dataset_path = config.get("GENERAL", "dataset_path")
        self.frequency_in_mins = config.getint("SCHEDULER", "frequency_in_mins")
        self.num_runners = config.getint("SCHEDULER", "num_runners")
        self.pool = Pool(processes=self.num_runners)
        self.runners = [DMLRunner(config_manager) for _ in range(self.num_runners)]
        self.current_jobs = [None]*self.num_runners
        self.results = [None]*self.num_runners
        self.event = Event()
        logging.info("Scheduler is set up!")

    def add_job(self, dml_job):
        """ Add a job to the queue"""
        assert type(dml_job) is DMLJob, "Job is not of type DMLJob."
        logging.info("Scheduling job...")
        self.queue.append(dml_job)

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
