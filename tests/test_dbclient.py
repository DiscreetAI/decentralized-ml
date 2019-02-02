import os
import tests.context
import psycopg2
import pytest
import pandas as pd
import configparser

from core.db_client import DBClient


@pytest.fixture(scope='session')
def config():
    config = configparser.ConfigParser()
    config.read('tests/artifacts/db_client/configuration.ini')
    return config

@pytest.fixture(scope='session')
def db_client(config):
    """
    Maintain instance of DB Client
    """
    return DBClient(config)

def test_get_data_providers_with_category(db_client):
    """
    Check that retrieving classifications with specified category works.
    """
    actual = db_client.get_data_providers_with_category('social_media')
    assert list(actual['data_provider'])[-1] == 'njkferwarif'
    assert list(actual['category'])[-1] == 'social_media'
