import pandas as pd

from core.db_client import DBClient


class DatasetClassifier(object):
	def __init__(self, label=None):
		self.label = label
		self.db_client = DBClient()

	def _classify_dataset(self):
		if not self.label:
			raise Exception('Classifier is not working at this time.')
		return self.label

	def label_dataset(self, name):
		label = self._classify_dataset()
		self.db_client.add_labels([name], [label])

