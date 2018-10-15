class EDComponent(object):
	"""
	Exploratory Data Component

	This component enables visualization for DataFrame.

	- 
	""" 

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

	def compare_using_histograms(self, df1, df2, column1, column2):
		"""
		Plots a scatter plot using, in order to compare them. 

		@param pandas Dataframe df_first:
		@param pandas Dataframe df_second:
		@param str column1: name of the first column
		@param str column2: name of the second column
		"""
		# TODO: get creative with plots 
		ax = df1.plot.scatter(column1)
		return df2.plot.scatter(column2, ax=ax)

	def compare_statistics(self, df1, df2, column1, column2):
		"""
		Returns the statistics for each dataframe's corresponding column.
		This can only work if the columns correspond to numerical values.

		@param pandas Dataframe df_first:
		@param pandas Dataframe df_second:
		@param str column1: name of the first column
		@param str column2: name of the second column
		"""
		# TODO: get creative with plots 
		return df1.describe(column1), df2.describe(column2)
