import os
import tests.context
import psycopg2
import pytest
import pandas as pd
from core.DBManager import DBManager

@pytest.fixture
def db_manager():
	return DBManager(config_filepath='tests/artifacts/database_config.json')

def test_empty_category_labels(db_manager):
	expected = pd.DataFrame(columns=['data_provider', 'category'])
	actual = db_manager.get_labels()
	assert expected.equals(actual)

def test_add_works(db_manager):
	db_manager._reset()
	row = {
			'data_provider': ['Facebook Profile Data'],
			'category': ['social_media']
		} 
	expected = pd.DataFrame(data=row)
	db_manager.add_labels(['Facebook Profile Data'], ['social_media'])
	actual = db_manager.get_labels()
	print(actual)
	print(expected)
	assert expected.equals(actual)

def test_get_data_providers_with_category(db_manager):
	db_manager._reset()
	row = {
			'data_provider': ['Facebook Profile Data'],
			'category': ['social_media']
		} 
	expected = pd.DataFrame(data=row)
	db_manager.add_labels(['Facebook Profile Data', 'Fitbit Calories Burned'], ['social_media', 'fitness'])
	actual = db_manager.get_data_providers_with_category('social_media')
	print(actual)
	print(expected)
	assert expected.equals(actual)


