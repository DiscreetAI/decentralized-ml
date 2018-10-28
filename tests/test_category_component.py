import pytest
import pandas as pd 
import numpy as np 
from core.category_component import CategoryComponent


@pytest.fixture
def blockchain_client():
	class BlockchainClient:
		def getter(self, provider):
			if provider == 'fruit':
				return {'dataset0': {'fruit': 'Apple','size': 'Large','color': 'Red'},
						'dataset1': {'fruit': 'Orange','size': 'Medium','color': 'Purple'},
						'dataset2': {'fruit': 'Berries','size': 'Mini','color': 'Orange'},
						'dataset3': {'fruit': 'Grapes','size': 'XL','color': 'Yellow'},
						'dataset4': {'fruit': 'Candy','size': 'Small','color': 'Red'},
						'dataset5': {'fruit': 'Chocolate','size': 'Large','color': 'Blue'},
						'dataset6': {'fruit': 'Bla','size': 'Small','color': 'Green'}}
			else:
				return {'dataset0': {'real': 10, 'barca': 0},
						'dataset1': {'real': 2, 'barca': 4},
						'dataset2': {'real': 0, 'barca': 20},
						'dataset3': {'real': 1, 'barca': 3},
						'dataset4': {'real': 0, 'barca': 4},
						'dataset5': {'real': 9, 'barca': 7},
						'dataset6': {'real': 1, 'barca': 6}}
	return BlockchainClient()

@pytest.fixture
def db_client():
	class DBClient:
		def _get_data_providers_with_category(self, category):
			if category == 'success':
				df = pd.DataFrame(columns=['data_provider'])
				df['data_provider'] = ['fruit', 'games']
				return df
			elif category == 'failure':
				return pd.DataFrame({'data_provider' : []})
			else:
				raise Exception('error')
	return DBClient()

def test_success(blockchain_client, db_client):
	"""
	Tests that category_component's expected value with success
	by checking all of the data in the dictionary returned by 
	get_ed_with_category.
	"""
	CC = CategoryComponent(db_client, blockchain_client)
	CC_dict = CC.get_ed_with_category('success')
	assert(CC_dict['Success'] == True)
	assert(CC_dict['Result'] == 
		[{'dataset0_fruit': ('fruit', {'fruit': 'Apple', 'size': 'Large', 'color': 'Red'})},
		 {'dataset1_fruit': ('fruit', {'fruit': 'Orange', 'size': 'Medium', 'color': 'Purple'})}, 
		 {'dataset2_fruit': ('fruit', {'fruit': 'Berries', 'size': 'Mini', 'color': 'Orange'})}, 
		 {'dataset3_fruit': ('fruit', {'fruit': 'Grapes', 'size': 'XL', 'color': 'Yellow'})}, 
		 {'dataset4_fruit': ('fruit', {'fruit': 'Candy', 'size': 'Small', 'color': 'Red'})}, 
		 {'dataset5_fruit': ('fruit', {'fruit': 'Chocolate', 'size': 'Large', 'color': 'Blue'})},
		 {'dataset6_fruit': ('fruit', {'fruit': 'Bla', 'size': 'Small', 'color': 'Green'})}, 
		 {'dataset0_games': ('games', {'real': 10, 'barca': 0})},
		 {'dataset1_games': ('games', {'real': 2, 'barca': 4})},
		 {'dataset2_games': ('games', {'real': 0, 'barca': 20})},
		 {'dataset3_games': ('games', {'real': 1, 'barca': 3})},
		 {'dataset4_games': ('games', {'real': 0, 'barca': 4})},
		 {'dataset5_games': ('games', {'real': 9, 'barca': 7})},
		 {'dataset6_games': ('games', {'real': 1, 'barca': 6})}])


def test_failure(blockchain_client, db_client): 
	"""
	Tests that category_component's expected value with failure
	by checking all of the data in the dictionary returned by 
	get_ed_with_category.
	"""
	CC = CategoryComponent(db_client, blockchain_client)
	CC_dict = CC.get_ed_with_category('failure')
	assert(CC_dict['Success'] == False)
	assert(CC_dict['Error'] == 'Category: failure has no data providers.')


def test_exception(blockchain_client, db_client): 
	"""
	Tests that category_component's expected value with exception
	by checking all of the data in the dictionary returned by 
	get_ed_with_category.
	"""
	CC = CategoryComponent(db_client, blockchain_client)
	CC_dict = CC.get_ed_with_category('exception')
	assert(CC_dict['Success'] == False)
	assert(CC_dict['Error'] == str(Exception('error')))




