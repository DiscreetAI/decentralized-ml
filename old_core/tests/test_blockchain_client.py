import tests.context
import pytest
import configparser

from core.blockchain_client import BlockchainClient


@pytest.fixture(scope='session')
def config():
    config = configparser.ConfigParser()
    config.read('tests/artifacts/blockchain_client/configuration.ini')
    return config

@pytest.fixture(scope='session')
def blockchain_client(config):
    """
    Maintain instance of Blockchain Client
    """
    return BlockchainClient(config)

def test_blockchain_client_empty(blockchain_client):
    """
    Check that retrieving labels with ineligible category raises an AssertionError.
    """
    with pytest.raises(AssertionError):
        blockchain_client.get_dataset('no_key')

def test_blockchain_client_post_and_get(blockchain_client):
    """
    Check that retrieving labels with specified category works.
    """
    blockchain_client.post_dataset('some_data', 'some_content')
    assert blockchain_client.get_dataset('some_data') == 'some_content'

# TODO: Update Blockchain Client and uncomment these tests.
