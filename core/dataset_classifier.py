import pandas as pd

from core.db_client import DBClient


class DatasetClassifier(object):
	
	def __init__(self):
		"""
		Initalizes instance of Dataset Classifier. Only 
		"""
		self.db_client = DBClient()

	def label_dataset(self, name=None, label=None):
		"""
		Labels dataset in DB. Only supports hardcoded names and labels at this time.
		"""
		if name and label:
			self.db_client.add_labels([name], [label])
		else:
			raise Exception('Classifier is not working at this time.')

