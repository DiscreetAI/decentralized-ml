from core.dataset import Dataset

import pandas as pd


class CategoryComponent(object):
	"""
	CategoryComponent

	- Returns the object containing datasets needed by __init__.py.
	""" 
	def __init__(self, db_client, blockchain_client):
		"""
		Initialize CategoryComponent instance.

		@param DBClient obj DBClient: object to be used for querying
		"""
		self.db_client = db_client
		self.blockchain_client = blockchain_client
		
	def get_datasets_with_category(self, category):
		"""
		Return list of Dataset objects for each data provider with the given 
		category.
 
		@param str category: name of the data category of interest
		@return dict: a dictionary with status and Error (str) or list of
					  Dataset objects.

		TODO: Need to resolve how to integrate the Category Component with the Blockchain Client. 
		Furthermore, we must check the return value of the getter method and work with it accordingly.
		TODO: Parsing and handling the parameters for bc.getter().
		"""
		try:
			data_providers_df = self.db_client.get_data_providers_with_category(category)
		except Exception as e:
			return {'success': False, 'error': str(e)}
		if data_providers_df.empty: 
			error_message = 'Category: {} has no data providers.'
			return {'success': False, 'error': error_message.format(category)}
		providers_list = data_providers_df['data_provider']
		datasets = list()
		uuid_to_dataset = dict()

		for provider in providers_list:
			ed_directory = self.blockchain_client.get_dataset(provider)
			for item in ed_directory.items():
				dataset = Dataset(item)
				datasets.append(dataset)
				uuid_to_dataset[dataset.uuid] = dataset
				
		return	{
				'success': True, 
				'datasets': datasets,
				'uuid_to_dataset': uuid_to_dataset
				}
