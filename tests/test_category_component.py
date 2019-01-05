import pytest
import pandas as pd 
import numpy as np 
from core.category_component import CategoryComponent


@pytest.fixture(scope='session')
def fruit_df():
	df = pd.DataFrame()
	df['fruit'] = ['Apple']
	df['size'] = ['Large']
	df['color'] = ['red']
	return df

@pytest.fixture(scope='session')
def futbol_df():
	df = pd.DataFrame()
	df['real'] = [5]
	df['barc'] = [0]
	return df	

@pytest.fixture(scope='session')
def fruit_result(fruit_df):
	fruit_dict = {}

	key = 'dataset1'
	fruit_dict[key] = (fruit_df.to_json(), fruit_df.describe().to_json())

	key = 'dataset2'
	fruit_dict[key] = (fruit_df.to_json(), fruit_df.describe().to_json())

	return fruit_dict

@pytest.fixture(scope='session')
def futbol_result(futbol_df):
	futbol_dict = {}

	key = 'dataset3'
	futbol_dict[key] = (futbol_df.to_json(), futbol_df.describe().to_json())

	key = 'dataset4'
	futbol_dict[key] = (futbol_df.to_json(), futbol_df.describe().to_json())

	return futbol_dict

@pytest.fixture(scope='session')
def blockchain_client(fruit_result, futbol_result):
	class BlockchainClient:
		def get_dataset(self, provider):
			if provider == 'fruit':
				return fruit_result
			else:
				return futbol_result
	return BlockchainClient()

@pytest.fixture(scope='session')
def db_client():
	class DBClient:
		def get_data_providers_with_category(self, category):
			if category == 'success':
				df = pd.DataFrame(columns=['data_provider'])
				df['data_provider'] = ['fruit', 'games']
				return df
			elif category == 'failure':
				return pd.DataFrame()
			else:
				raise Exception('error')
	return DBClient()

@pytest.fixture(scope='session')
def category_component(blockchain_client, db_client):
	return CategoryComponent(db_client, blockchain_client)

def test_success(category_component, fruit_df, futbol_df):
	"""
	Tests that category_component's expected value with success
	by checking all of the data in the dictionary returned by 
	get_datasets_with_category.
	"""
	category_component_dict = category_component.get_datasets_with_category('success')
	assert category_component_dict ['Success']
	result = category_component_dict['Result']
	assert len(result) == 4, 'Four datasets should have been found'
	first, second, third, fourth = result
	assert first.uuid == 'dataset1' \
		and first.sample.sort_index(axis=1).equals(fruit_df.sort_index(axis=1))
	assert second.uuid == 'dataset2' \
		and second.sample.sort_index(axis=1).equals(fruit_df.sort_index(axis=1))
	assert third.uuid == 'dataset3' \
		and third.sample.sort_index(axis=1).equals(futbol_df.sort_index(axis=1))
	assert fourth.uuid == 'dataset4' \
		and fourth.sample.sort_index(axis=1).equals(futbol_df.sort_index(axis=1))

def test_failure(category_component): 
	"""
	Tests that category_component's expected value with failure
	by checking all of the data in the dictionary returned by 
	get_datasets_with_category.
	"""
	category_component_dict = category_component.get_datasets_with_category('failure')
	assert not category_component_dict['Success']
	assert category_component_dict['Error'] == 'Category: failure has no data providers.'


def test_exception(category_component): 
	"""
	Tests that category_component's expected value with exception
	by checking all of the data in the dictionary returned by 
	get_datasets_with_category.
	"""
	category_component_dict = category_component.get_datasets_with_category('exception')
	assert not category_component_dict['Success']
	assert category_component_dict['Error'] == 'error'




