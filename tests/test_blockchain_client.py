import tests.context
import pytest

from core.blockchain_client import BlockchainClient

@pytest.fixture
def blockchain_client():
    """
    Maintain instance of Blockchain Client
    """
    return BlockchainClient(
        config_filepath='tests/artifacts/blockchain_client/blockchain_config.json'
    )

def test_blockchain_client_empty(blockchain_client):
    """
    Check that retrieving labels with specified category works.
    """
    assert blockchain_client.get_dataset('some_data') == ''

def test_blockchain_client_post_and_get(blockchain_client):
    """
    Check that retrieving labels with specified category works.
    """
    blockchain_client.post_dataset('some_data', 'some_content')
    assert blockchain_client.get_dataset('some_data') == 'some_content'
