import tests.context	
import pytest	

from core.configuration                 import ConfigurationManager	
from core.blockchain.blockchain_gateway import BlockchainGateway
from core.utils.enums                   import RawEventTypes
from core.blockchain.blockchain_utils   import setter, TxEnum


@pytest.fixture	
def config_manager():	
    config_manager = ConfigurationManager()
    config_manager.bootstrap(	
        config_filepath='tests/artifacts/blockchain/configuration.ini'	
    )	
    return config_manager	

@pytest.fixture
def communication_manager():		
    class MockCommunicationManager:
        def __init__(self):
            self.dummy1 = None
            self.dummy2 = None
        def inform(self, dummy1, dummy2):
            self.dummy1 = dummy1
            self.dummy2 = dummy2
    return MockCommunicationManager()

@pytest.fixture	
def blockchain_gateway(config_manager, communication_manager):	
    blockchain_gateway = BlockchainGateway()
    blockchain_gateway.configure(config_manager, communication_manager)
    return blockchain_gateway	

def test_blockchain_gateway_can_be_initialized(config_manager, communication_manager):	
    blockchain_gateway = BlockchainGateway()
    assert blockchain_gateway is not None	

def test_blockchain_gateway_can_listen_decentralized_learning(config_manager, communication_manager):
    """
    Uses Mock Communication Manager to ensure that the Gateway
    can listen for decentralized learning.
    This test has some problems since the loop of events is incomplete.
    # NOTE: Should be updated after Averaging/Communication PRs are merged
    """
    
    blockchain_gateway = BlockchainGateway()
    blockchain_gateway.configure(config_manager, communication_manager)
    tx_receipt = setter(blockchain_gateway.client, None, blockchain_gateway.port, {"model": "hello world"}, True)
    assert tx_receipt
    blockchain_gateway._listen(blockchain_gateway._handle_new_session_creation,
        blockchain_gateway._filter_new_session)
    # at this point we should listen for decentralized learning, hear it, and update our communication manager
    assert communication_manager.dummy1 == RawEventTypes.NEW_SESSION.name, "Wrong dummy1"
    assert communication_manager.dummy2 == {"model": "hello world"}, "Wrong dummy2"

# TODO: This will be implemented once we figure out how.	
# def test_handle_decentralized_learning(blockchain_gateway):	
#     """To be implemented."""
#     pass	
# def test_listen_new_weights(blockchain_gateway):	
#     """To be implemented."""	
#     pass	
# def test_handle_new_weights(blockchain_gateway):	
#     """To be implemented."""	
#     pass	
# def test_listen_terminate(blockchain_gateway):	
#     """To be implemented."""	
#     pass	
# def test_handle_terminate(blockchain_gateway):	
#     """To be implemented."""	
#     pass
