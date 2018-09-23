"""Use class CategoryComponent(object) to have compatibility between Python 2 and 3. 
   For now on, write code to be Python agnostic. """

""" Requirements: 
	1. Have an instance of DBClient. Handle this in initialization.
	2. Have a method that receives a category (in string format, perhaps). 
		And use the BDClient instance to get a list of data providers. 
		And then gets the ED list from Blockchain.
	3. Sends this to the ED component or perhaps the ED component has an instance
	   of the Category Component.
	3. List of data providers will then be passed to the blockchain and receive 
		the ED for each data provider. 
"""

""" DBClient.py could:
	1. Specified the return values, perhaps instead of saying list
	specified that is is a DataFrame (pandas).
	e.g.
	@param str category: name of the data category of interest
    @return dict: a dictionary with status and Error or Directory
    @raises ValueError: incorrect value
"""

""" import Blockchain** as bc"""
import pandas as pd

class CategoryComponent(object):
	"""
	CategoryComponent

	- 
	""" 
	def __init__(self, DBClient=None):
		"""
		Initialize CategoryComponent instance.

		@param DBClient obj DBClient: object to be used for querying

		TODO: 
		1. What do to when DBClient instance is null?
		PROPOSAL: Why/how/could this happen?
		If it can happen then an alternative could be to take a config_filepath
		and create a DBClient instance.
		"""
		self.DBClient = DBClient

	def get_ed_with_category(self, category):
		"""
  		Return ED for each data provider with the given category.

    	@param str category: name of the data category of interest
    	@return dict: a dictionary with status and Error (str) or Directory (insert data_providers_ed type)

    	TODO:
    	1. type of data_providers_ed is yet to be known
    	2. dictionary structure FAILURE vs SUCESS or 400 vs 200 should be determined, 
    	get feedback on what they would like, we could simply return None vs data_providers_ed.
    	I cannot visualize a need for a dictionary, yet.
    	3. the name of this function is not that descriptive
		"""
		try:
        	data_providers_df = self.DBClient._get_data_providers_with_category(category)
        	data_providers_ed = bc.get_data_providers_ED(data_providers_df)
        	return {'Status': 'SUCCESS', 'Directory': data_providers_ed}
    	except Exception as e:
    		return {'Status': 'FAILURE', 'Error': 'Invalid category'}





