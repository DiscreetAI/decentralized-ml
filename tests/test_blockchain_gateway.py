import tests.context	
import pytest	
import ipfsapi

from core.configuration                 import ConfigurationManager	
from core.blockchain.blockchain_gateway import BlockchainGateway
from core.utils.enums                   import RawEventTypes, MessageEventTypes
from core.blockchain.blockchain_utils   import setter, TxEnum
from core.utils.dmljob                  import deserialize_job, serialize_job
from tests.testing_utils import make_initialize_job, make_model_json


@pytest.fixture(scope='session')
def config_manager():	
    config_manager = ConfigurationManager()
    config_manager.bootstrap(	
        config_filepath='tests/artifacts/blockchain/configuration.ini'	
    )	
    return config_manager	

@pytest.fixture(scope='session')
def ipfs_client(config_manager):
    config = config_manager.get_config()
    return ipfsapi.connect(config.get('BLOCKCHAIN', 'host'), 
                            config.getint('BLOCKCHAIN', 'ipfs_port'))

@pytest.fixture(scope='session')
def communication_manager():		
    class MockCommunicationManager:
        def __init__(self):
            self.dummy_msg_type = "None"
            self.data_provider_info = "None"
            self.job_info = "None"
        def inform(self, dummy1, payload):
            self.dummy_msg_type = dummy1
            self._create_session(payload)
        def _create_session(self, payload):
            assert payload.get(TxEnum.KEY.name) is MessageEventTypes.NEW_SESSION.name, \
                "Expected a new session but got {}".format(payload.get(TxEnum.KEY.name))
            initialization_payload = payload.get(TxEnum.CONTENT.name)
            self._setup_optimizer(initialization_payload)
        def _setup_optimizer(self, initialization_payload):
            self.data_provider_info = initialization_payload.get(TxEnum.KEY.name)
            self.job_info = initialization_payload.get(TxEnum.CONTENT.name)
            serialized_job = self.job_info.get('serialized_job')
            self.job = deserialize_job(serialized_job)
            self.job.uuid = self.data_provider_info.get("dataset_uuid")
            self.job.label_column_name = self.data_provider_info.get(
                "label_column_name")
            assert self.job.uuid, "uuid of job not set!"
        def reset(self):
            self.dummy_msg_type = "None"
            self.data_provider_info = "None"
            self.job_info = "None"
    return MockCommunicationManager()

@pytest.fixture(scope='session')
def dataset_manager():
    class MockDatasetManager:
        def __init__(self):
            self.mappings = {1357: "hello"}
        def validate_key(self, key):
            return key in self.mappings.keys()
    return MockDatasetManager()

@pytest.fixture	(scope='session')
def blockchain_gateway(
    config_manager, communication_manager, ipfs_client, dataset_manager):	
    blockchain_gateway = BlockchainGateway()
    blockchain_gateway.configure(config_manager, communication_manager, 
                                ipfs_client, dataset_manager)
    return blockchain_gateway	

def test_blockchain_gateway_can_be_initialized(
    config_manager, communication_manager):	
    blockchain_gateway = BlockchainGateway()
    assert blockchain_gateway is not None	

def test_blockchain_gateway_filters_sessions(
    blockchain_gateway, communication_manager):
    """
    Ensures that the gateway won't intercept messages not intended for it
    """
    serialized_job = serialize_job(make_initialize_job(make_model_json()))
    new_session_event = {
        "optimizer_params": "",
        "serialized_job": serialized_job
    }
    tx_receipt = setter(
        blockchain_gateway._client, 
        {"dataset_uuid": 5678, "label_column_name": "label"},
        blockchain_gateway._port, 
        new_session_event, 
        flag=True
    )
    assert tx_receipt
    blockchain_gateway._listen(blockchain_gateway._handle_new_session_creation,
        blockchain_gateway._filter_new_session)
    # at this point we should listen for decentralized learning
    # not hear it (filter_new_session() == False)
    # and therefore not update our communication manager
    assert communication_manager.dummy_msg_type == "None", \
        "Shouldn't have heard anything but heard a message with uuid {}".format(
            communication_manager.job.uuid)
    assert communication_manager.data_provider_info == "None", \
        "Shouldn't have heard anything!"
    assert communication_manager.job_info == "None", \
        "Shouldn't have heard anything!"

def test_blockchain_gateway_can_listen_decentralized_learning(
    blockchain_gateway, communication_manager):
    """
    Uses Mock Communication Manager to ensure that the Gateway
    can listen for decentralized learning.
    """
    serialized_job = serialize_job(make_initialize_job(make_model_json()))
    new_session_event = {
        "optimizer_params": "this cannot be empty",
        "serialized_job": serialized_job
    }
    tx_receipt = setter(
        blockchain_gateway._client, 
        {"dataset_uuid": 1357, "label_column_name": "label"},
        blockchain_gateway._port, 
        new_session_event, 
        True
    )
    assert tx_receipt
    blockchain_gateway._listen(blockchain_gateway._handle_new_session_creation,
        blockchain_gateway._filter_new_session)
    # at this point we should listen for decentralized learning
    # hear it (filter_new_session() == True)
    # and update our communication manager
    assert communication_manager.dummy_msg_type == RawEventTypes.NEW_MESSAGE.name, \
        "Wrong msg_type"
    assert communication_manager.data_provider_info == {
        "dataset_uuid": 1357, "label_column_name": "label"
    }
    communication_manager.reset()

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
