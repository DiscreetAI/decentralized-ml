import tests.context
import ipfsapi
import pytest

from core.blockchain.blockchain_utils import *
from core.configuration import ConfigurationManager


@pytest.fixture
def config():
    config_manager = ConfigurationManager()
    config_manager.bootstrap(
        config_filepath='tests/artifacts/blockchain/configuration.ini'
    )
    return config_manager.get_config()

@pytest.fixture
def ipfs_client(config):
    return ipfsapi.connect(config.get('BLOCKCHAIN', 'host'), config.getint('BLOCKCHAIN', 'ipfs_port'))


def test_blockchain_utils_getter_nonexistent_key(config, ipfs_client):
    get_val = getter(
        ipfs_client,
        config.get('BLOCKCHAIN', 'test_nonexistent_key'),
        [],
        config.getint('BLOCKCHAIN', 'http_port'),
        config.getint('BLOCKCHAIN', 'timeout')
        )
    assert get_val == []

def test_blockchain_utils_setter_simple(config, ipfs_client):
    get_val_before = getter(
        ipfs_client,
        config.get('BLOCKCHAIN', 'test_single_key'),
        [],
        config.getint('BLOCKCHAIN', 'http_port'),
        config.getint('BLOCKCHAIN', 'timeout')
        )
    setter(ipfs_client,
        config.get('BLOCKCHAIN', 'test_single_key'),
        config.getint('BLOCKCHAIN', 'http_port'),
        config.get('BLOCKCHAIN', 'test_value'),
        )
    get_val_after = getter(
        ipfs_client,
        config.get('BLOCKCHAIN', 'test_single_key'),
        [],
        config.getint('BLOCKCHAIN', 'http_port'),
        config.getint('BLOCKCHAIN', 'timeout')
        )
    assert get_val_after == get_val_before + ["'World!'"]

def test_blockchain_utils_setter_multiple_values(config, ipfs_client):
    get_val_before = getter(
        ipfs_client,
        config.get('BLOCKCHAIN', 'test_multiple_key'),
        [],
        config.getint('BLOCKCHAIN', 'http_port'),
        config.getint('BLOCKCHAIN', 'timeout')
        )
    setter(ipfs_client,
        config.get('BLOCKCHAIN', 'test_multiple_key'),
        config.getint('BLOCKCHAIN', 'http_port'),
        config.get('BLOCKCHAIN', 'test_value'),
        )
    setter(ipfs_client,
        config.get('BLOCKCHAIN', 'test_multiple_key'),
        config.getint('BLOCKCHAIN', 'http_port'),
        config.get('BLOCKCHAIN', 'test_value'),
        )
    get_val_after = getter(
        ipfs_client,
        config.get('BLOCKCHAIN', 'test_multiple_key'),
        [],
        config.getint('BLOCKCHAIN', 'http_port'),
        config.getint('BLOCKCHAIN', 'timeout')
        )
    assert get_val_after == get_val_before + ["'World!'", "'World!'"]
