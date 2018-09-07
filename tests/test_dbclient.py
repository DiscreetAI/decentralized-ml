import os
import tests.context
import psycopg2
import pytest
import pandas as pd
from core.db_client import DBClient

@pytest.fixture
def db_client():
	return DBClient(config_filepath='tests/artifacts/db_client/database_config.json')

def check_empty_category_labels(db_client):
	expected = pd.DataFrame(columns=['data_provider', 'category'])
	actual = db_client.get_labels()
	assert expected.equals(actual)

def check_add_works(db_client):
	actual = db_client.get_labels()
	assert list(actual['data_provider']) == ['Facebook Profile Data']
	assert list(actual['category']) == ['social_media']

def check_get_data_providers_with_category(db_client):
	actual = db_client.get_data_providers_with_category('social_media')
	assert list(actual['data_provider']) == ['Facebook Profile Data']
	assert list(actual['category']) == ['social_media']

def test_end_to_end(db_client):
	db_client.reset()
	check_empty_category_labels(db_client)
	db_client.add_labels(['Facebook Profile Data'], ['social_media'])
	check_add_works(db_client)
	db_client.add_labels(['Fitbit Calories Burned'], ['fitness'])
	check_get_data_providers_with_category(db_client)
	db_client.reset()
