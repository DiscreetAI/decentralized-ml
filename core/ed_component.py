import pandas as pd

class EDComponent(object):
	"""
	Exploratory Data Component

	This component enables visualization for DataFrame.

	- 
	""" 
	def __init__(self):
		pass

	def histogram(self, df, column):
		"""
		Plots a histogram of the column from the Dataframe. 

		@param pandas Dataframe df:
		@param str column: name of the column to plot
		"""
		return df.hist(column)

	def scatter(self, df, column1, column2):
		"""
		Plots a scatter plot using, in order to compare them. 

		@param pandas Dataframe df:
		@param str column1: name of the first column
		@param str column2: name of the second column
		"""
		return df.plot.scatter(column1, column2)

	def compare(self, df1, df2, column1, column2):
		"""
		Plots a scatter plot using, in order to compare them. 

		@param pandas Dataframe df_first:
		@param pandas Dataframe df_second:
		@param str column1: name of the first column
		@param str column2: name of the second column
		"""
		# TODO: get creative with plots 
		ax = df1.plot.scatter(column1)
		return df2.plot.scatter(column2)

	def compare2(self, df1, df2, column1, column2):
		"""
		Plots the average and STDev of both columns sets.
		This can only work if the columns correspond to numerical values.

		@param pandas Dataframe df_first:
		@param pandas Dataframe df_second:
		@param str column1: name of the first column
		@param str column2: name of the second column
		"""
		# TODO: get creative with plots 
		pass
