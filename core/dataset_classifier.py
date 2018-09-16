import pandas as pd

from core.db_client import DBClient


class DatasetClassifier(object):
	"""
	DatasetClassifier

	-Sets up framework for what classification will look like when we actually have a trained classifier
	-For now, can be used to manually add labels to datasets (or just use DB client, TBD)
	-Didn't write tests since it's not the long term option and the main functionality (posting to DB) is tested under DBClient
	-Eventually will be called by DatasetManager after transform is completed
	"""
	def __init__(self, db_client):
		"""
		Initalizes instance of Dataset Classifier.
		"""
		self.db_client = db_client

	def label_dataset(self, name=None, label=None):
		"""
		Labels dataset in DB. Only supports hardcoded names and labels at this time.
		"""
		if name and label:
			self.db_client.add_labels([name], [label])
		else:
			raise Exception('Classifier is not working at this time.')

