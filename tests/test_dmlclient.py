import tests.context
import pytest
import configparser

from keras.models import Sequential
from keras.layers import Dense, Activation

from core.dml_client import DMLClient

@pytest.fixture(scope='session')
def config():
    config = configparser.ConfigParser()
    config.read('tests/artifacts/blockchain_client/configuration.ini')
    return config

@pytest.fixture(scope='session')
def dml_client(config):
    """
    DMLClient instance
    """
    return DMLClient(config)

@pytest.fixture(scope='session')
def ipfs_client(dml_client):
    """
    IPFS Client instance
    """
    return dml_client.client

@pytest.fixture(scope='session')
def model():
    """
    Returns a model in Keras that has been compiled with its optimizer
    """
    model = Sequential([
        Dense(32, input_shape=(784,)),
        Activation('relu'),
        Dense(10),
        Activation('softmax'),
    ])
    model.compile(optimizer='rmsprop',
                  loss='mse')
    return model

@pytest.fixture(scope='session')
def participants():
    """
    Returns an example dict of participants
    """
    return [{"dataset_uuid": 1234, "label_column_name": "label"}, 
            {"dataset_uuid": 4567, "label_column_name": "label"}]

def test_dml_client_serializes_job_correctly(dml_client, ipfs_client, model, participants):
    key = dml_client.decentralized_learn(
        model, participants
    )
    content = ipfs_client.get_json(key)["CONTENT"]
    true_model_json = model.to_json()
    assert true_model_json == content["serialized_job"]["serialized_model"]
    assert participants == content["participants"]
    assert content["optimizer_params"]["optimizer_type"] == "FEDERATED_AVERAGING"

def test_dml_client_validates_label_column_name(dml_client, model, participants):
    participants.append({"dataset_uuid": 666})
    with pytest.raises(Exception):
        key = dml_client.decentralized_learn(
            model, participants
        )
    