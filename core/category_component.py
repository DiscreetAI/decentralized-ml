import pandas as pd


class CategoryComponent(object):
	"""
	CategoryComponent

	- Returns the object containing datasets needed by __init__.py.
	""" 
	def __init__(self, DBClient, BCClient):
		"""
		Initialize CategoryComponent instance.

		@param DBClient obj DBClient: object to be used for querying
		"""
		self.DBClient = DBClient
		self.BCClient = BCClient
		
	def get_ed_with_category(self, category):
		"""
		Return list of dictionaries for each data provider with the given category.
		Each dictionary has the following structure: 
			key: #_data_provider, where # stands for the dataset number/index.
			value: (data_provider, dataset json object), this is a tuple.
 
		@param str category: name of the data category of interest
		@return dict: a dictionary with status and Error (str) or Directory with data providers ED

		TODO: Need to resolve how to integrate the Category Component with the Blockchain Client. 
		Furthermore, we must check the return value of the getter method and work with it accordingly.
		TODO: Parsing and handling the parameters for bc.getter().
		"""
		try:
			data_providers_df = self.DBClient._get_data_providers_with_category(category)
		except Exception as e:
			return {'Success': False, 'Error': str(e)}
		if data_providers_df.empty: 
			return {'Success': False, 'Error': 'Category: {} has no data providers.'.format(category)}
		providers_list = data_providers_df['data_provider']
		result = list()
		for provider in providers_list:
			datasets_dict = self.BCClient.getter(provider)
			datasets = list(datasets_dict.values())
			for index in range(len(datasets)):
				key = 'dataset{0}_{1}'.format(index, provider)
				value = (provider, datasets[index])
				result.append({key: value})
		return {'Success': True, 'Result': result}
