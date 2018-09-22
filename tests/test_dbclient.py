import os
import tests.context
import psycopg2
import pytest
import pandas as pd
from core.db_client import DBClient

@pytest.fixture
def db_client():
    """
    Maintain instance of DB Client
    """
    return DBClient(
        config_filepath='tests/artifacts/db_client/database_config.json'
    )

def test_get_data_providers_with_category(db_client):
    """
    Check that retrieving labels with specified category works.
    """
    actual = db_client._get_data_providers_with_category('social_media')
    assert list(actual['data_provider'])[-1] == 'njkferwarif'
    assert list(actual['category'])[-1] == 'social_media'
