import os
import tests.context
import psycopg2
import pytest
import pandas as pd
import string
import random
from core.db_client import DBClient

@pytest.fixture
def db_client():
    """
    Maintain instance of DB Client
    """
    return DBClient(
        config_filepath='tests/artifacts/db_client/database_config.json'
    )

def check_empty_category_labels(db_client):
    """
    Check that retrieving labels works
    """
    expected = pd.DataFrame(columns=['data_provider', 'category'])
    actual = db_client._get_labels()
    assert expected.equals(actual)

def check_add_works(db_client, data_provider):
    """
    Check that adding labels works
    """
    actual = db_client._get_labels()
    assert list(actual['data_provider'])[-1] == data_provider
    assert list(actual['category'])[-1] == 'social_media'

def check_get_data_providers_with_category(db_client, data_provider):
    """
    Check that retrieving labels with specified category works.
    """
    actual = db_client._get_data_providers_with_category('social_media')
    assert list(actual['data_provider'])[-1] == data_provider
    assert list(actual['category'])[-1] == 'social_media'

def reset(db_client, data_provider_list):
    """
    Clean up before and after tests.
    """
    labels = db_client._get_labels()
    for data_provider in data_provider_list:
        labels = labels[labels['data_provider'] != data_provider]
    labels.to_sql(
        name=db_client.table_name, 
        con=db_client.db.engine, 
        if_exists='replace', 
        index=False
    )

def test_end_to_end(db_client):
    labels = pd.DataFrame(columns=['category', 'data_provider'])
    labels.to_sql(
        name=db_client.table_name, 
        con=db_client.db.engine, 
        if_exists='append', 
        index= False
    )
    def random_string(length):
        return ''.join(
            random.choice(string.ascii_letters) for m in range(length)
        ).lower()
    social_data_provider = random_string(10)
    fitness_data_provider = random_string(10)
    db_client.add_labels([social_data_provider], ['social_media'])
    check_add_works(db_client, social_data_provider)
    db_client.add_labels([fitness_data_provider], ['fitness'])
    check_get_data_providers_with_category(db_client, social_data_provider)
    reset(db_client, [social_data_provider, fitness_data_provider])
