class EDComponent(object):
	"""
	Exploratory Data Component

	- This component enables visualization for a dataframes.
	""" 

	def histogram(self, df, column):
		"""
		Generates a histogram of the column from the Dataframe. 

		@param pandas Dataframe df:
		@param str column: name of the column to plot
		"""
		return df.hist(column)

	def scatter(self, df, column1, column2):
		"""
		Generates a scatter plot, in order to compare the columns.
		The coordinates of each point are defined by
		two dataframe columns and filled circles are
		used to represent each point.  

		@param pandas Dataframe df:
		@param str column1: name of the first column
		@param str column2: name of the second column
		"""
		return df.plot.scatter(column1, column2)

	def scatter_compare(self, df1, df2, column1, column2):
		"""
		Generates a scatter plot using two dataframes.
		Both evaluations are on the same two columns.
		The coordinates of each point are defined by
		two dataframe columns and filled circles are
		used to represent each point. 

		@param pandas Dataframe df_first:
		@param pandas Dataframe df_second:
		@param str column1: name of the first column
		@param str column2: name of the second column
		"""
		ax = df1.plot.scatter(column1, column2)
		return df2.plot.scatter(column1, column2, ax=ax)
