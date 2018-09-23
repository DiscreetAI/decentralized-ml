import pandas as pd


def add_header(cols, filepath):
	"""
	Updates file at 'filepath' with 'cols' (an array of column names) 
	"""
	pd.read_csv(filepath, names=cols, header=None).to_csv(filepath, index=False)