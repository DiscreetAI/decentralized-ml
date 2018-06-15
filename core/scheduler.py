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
		self.current_runner = None
		self.queue = Queue()
		with open('core/config.json') as f:
    		self.dataset_path = json.load(f)["dataset_path"]

	def enqueue(dml_job):
		assert type(dml_job) is DMLJob, "Job is not of type DMLJob."
		self.queue.put(dml_job)
		if not self.current_runner:
			self._run_next_job()

	def _dequeue():
		return self.queue.get()

	def _run_next_job():
		current_job = self._dequeue()
		self.current_runner = DMLRunner(self.dataset_path, current_job.config)
		self.current_runner.run_job(current_job)
