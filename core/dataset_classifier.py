import pandas as pd


class DatasetClassifier(object):
	def __init__(self, label):
		self.label = label

	def classify_dataset(self):
		if not self.label:
			raise Exception('Classifier is not working at this time.')
		return self.label
