# Add the parent directory to the PATH to allow imports.
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from queue import Queue
import schedule
import time
import json

from core.utils.dmljob import DMLJob
from core.runner import DMLRunner


class DMLScheduler(object):
	"""
	DML Scheduler

	This class schedules and manages the execution of DMLJobs using the DMLRunner.
	Note: currently runs in only one thread.
	Note2: only supports one dataset type.

	"""

	def __init__(self):
		self.queue = Queue()
		with open('core/config.json') as f:
			config = json.load(f)
    		dataset_path = config["dataset_path"]
			run_frequency = config["scheduler_frequency_in_mins"]
			runner_config = config["runner_config"]
		self.current_runner = DMLRunner(dataset_path, runner_config)
		schedule.every(run_frequency).minutes.do(self._run_next_job_if_necessary())
		schedule.run_continuously()

	def enqueue(self, dml_job):
		assert type(dml_job) is DMLJob, "Job is not of type DMLJob."
		self.queue.put(dml_job)
		self._run_next_job_if_necessary()

	def _run_next_job_if_necessary(self):
		if not self.current_runner.is_active() and not self.queue.empty():
			self._run_next_job()

	def _run_next_job(self):
		current_job = self._dequeue()
		self.current_runner.run_job(current_job)

	def _dequeue(self):
		return self.queue.get()
