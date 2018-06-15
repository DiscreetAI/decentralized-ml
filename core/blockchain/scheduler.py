from queue import Queue

class Scheduler(object):
	def __init__(self):
		self.q = Queue()
	def enqueue(job):
		self.q.put(job)
	def dequeue():
		return self.g.get()