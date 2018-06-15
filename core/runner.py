# Add the parent directory to the PATH to allow imports.
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import logging
import random
import uuid

import numpy as np
import tensorflow as tf
import keras

from custom.keras import model_from_serialized, get_optimizer
from data.iterators import count_datapoints
from data.iterators import create_train_dataset_iterator
from data.iterators import create_test_dataset_iterator

from eth_utils import is_address
from solc import compile_source, compile_files
# from blockchain_utils import *

logging.basicConfig(level=logging.DEBUG,
                    format='[Runner] %(asctime)s %(levelname)s %(message)s')

# class ListenerDAG(object):
#     """
#     This class listens to its peers on the DAG network.
#     """
#     def __init__():



class ListenerEthereum(object):
    """
    This class listens to the deployed smart contract.
    """
    def __init__(self, iden, provider, clientAddress=None, delegatorAddress=None):

        self.web3 = provider
        # self.api = ipfsapi.connect('127.0.0.1', 5001)

        self.PASSPHRASE = 'panda'
        self.TEST_ACCOUNT = '0xb4734dCc08241B46C0D7d22D163d065e8581503e'
        self.TEST_KEY = '146396092a127e4cf6ff3872be35d49228c7dc297cf34da5a0808f29cf307da1'

        contract_source_path_A = "blockchain/Delegator.sol"
        contract_source_path_B = "blockchain/Query.sol"
        contract_source_path_C = "blockchain/DAgoraToken.sol"
        self.compiled_sol = compile_files([contract_source_path_A, contract_source_path_B,
        contract_source_path_C])

        self.iden = iden

        if clientAddress:
            assert(is_address(clientAddress))
            self.clientAddress = clientAddress
        else:
            #TODO: Initialize client 'container' address if it wasn't assigned one
            self.clientAddress = self.web3.personal.newAccount(self.PASSPHRASE)
            assert(is_address(self.clientAddress))
        self.web3.personal.unlockAccount(self.clientAddress, self.PASSPHRASE)
    
        print("Client Address:", self.clientAddress)

        self.Delegator_address = delegatorAddress
        self.DAgoraToken_address = self.web3.toChecksumAddress('0x1698215a2bea4935ba9e0f5b48347e83450a6774')

    def get_money(self):
        # get_testnet_eth(self, self.clientAddress, self.web3)
        print("Client balance:", self.web3.eth.getBalance(self.clientAddress))

        Query_id, self.Query_interface = self.compiled_sol.popitem()
        Delegator_id, self.Delegator_interface = self.compiled_sol.popitem()
        self.compiled_sol.popitem()
        self.compiled_sol.popitem()
        DAgoraToken_id, self.DAgoraToken_interface = self.compiled_sol.popitem()

        if self.Delegator_address:
            assert(is_address(self.Delegator_address))
        else:

            # self.Query_address = deploy_Query(self.web3, self.Query_interface, self.TEST_ACCOUNT, addr_lst)
            self.Delegator_address = deploy_Master(self.web3, self.Delegator_interface, self.clientAddress)
            print("Delegator Address", self.Delegator_address)

    def launch_query(self, target_address):
        contract_obj = self.web3.eth.contract(
           address=self.Delegator_address,
           abi=self.Delegator_interface['abi'])
        tx_hash = contract_obj.functions.query(target_address).transact(
            {'from': self.clientAddress})

        self.web3.eth.waitForTransactionReceipt(tx_hash)

        tx_receipt = self.web3.eth.getTransactionReceipt(tx_hash)
        # print(tx_receipt)
        self.Query_address = self.web3.toChecksumAddress('0x' + tx_receipt['logs'][0]['data'].split('000000000000000000000000')[2])
        # return tx_receipt

    def ping_client(self):
        contract_obj = self.web3.eth.contract(
           address=self.Query_address,
           abi=self.Query_interface['abi'])
        tx_hash = contract_obj.functions.pingClients().transact({'from': self.clientAddress})

        self.web3.eth.waitForTransactionReceipt(tx_hash)
        
        tx_receipt = self.web3.eth.getTransactionReceipt(tx_hash)
        return tx_receipt
    def handle_ClientSelected_event(self, event_data):

        e_data = [x for x in event_data.split('00') if x]

        IPFSaddress_receiving = bytearray.fromhex(e_data[3][1:]).decode()[1:]
        # address = self.web3.toChecksumAddress('0x' + e_data[1])
        # assert(self.clientAddress == address)
        print("IPFS address:", IPFSaddress_receiving)

        # IPFS cat from IPFS_receiving

        contract_obj = self.web3.eth.contract(
           address=self.Query_address,
           abi=self.Query_interface['abi'])

        #will be hardcoded
        config = {
            "num_clients": 1,
            "model_type": 'gan',
            "dataset_type": 'iid',
            "fraction": 1.0,
            "max_rounds": 1,
            "batch_size": 10,
            "epochs": 1,
            "learning_rate": 1e-4,
            "save_dir": './results/',
            "goal_accuracy": 1.0,
            "lr_decay": 0.99
        }

        # data = api.cat(IPFSaddress_receiving)

        # IPFS add
        updatedAddress, n_k = self.train(IPFSaddress_receiving, config)

        tx_hash = contract_obj.functions.receiveResponse(updatedAddress, n_k).transact(
            {'from': self.clientAddress})

        self.web3.eth.waitForTransactionReceipt(tx_hash)

        tx_receipt = self.web3.eth.getTransactionReceipt(tx_hash)
        log = contract_obj.events.ResponseReceived().processReceipt(tx_receipt)
        # return log[0]

    def handle_QueryCreated_event(self, event_data):
        print(event_data)
        address = event_data.split("000000000000000000000000")[2]
        assert(is_address(address))
        self.Query_address = self.web3.toChecksumAddress(address)
        return event_data.split("000000000000000000000000")
    async def start_listening(self, event_to_listen, poll_interval=5):
        while True:
            lst = event_to_listen.get_new_entries()
            if lst:
                # print(lst[0])
                return lst[0]
            await asyncio.sleep(poll_interval)

    def filter_set(self, event_sig, contract_addr, handler):
        event_signature_hash = self.web3.sha3(text=event_sig).hex()
        event_filter = self.web3.eth.filter({
            "address": contract_addr.lower(),
            "topics": [event_signature_hash]
            })
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        try:
            inter = loop.run_until_complete(
                self.start_listening(event_filter, 2))
            check = handler(inter['data'])
        finally:
            loop.close()
        return check

    def main(self):
        check = self.filter_set("QueryCreated(address,address)", self.Delegator_address, self.handle_QueryCreated_event)
        if check[0] + check[1] == self.clientAddress.lower():
            target_contract = check[0] + check[2]
            # print(target_contract)
            # retval = self.filter_set("ClientSelected(address,string)", target_contract, self.handle_ClientSelected_event)
            self.filter_set("ClientSelected(address,string)", target_contract, self.handle_ClientSelected_event)
            # return "I got chosen:", retval[0] + retval[1]
            # print("listening for next round to begin...")
            print("receiving reward...")
            contract_obj = self.web3.eth.contract(
            address=self.DAgoraToken_address,
            abi=self.DAgoraToken_interface['abi'])

            tx_hash = contract_obj.functions.transfer(self.clientAddress, 50000000).transact({'from': '0xf6419f5c5295a70C702aC21aF0f64Be07B59F3c4'})
            self.web3.eth.waitForTransactionReceipt(tx_hash)
            print('sent!')
            # print('Token Balance:', contract_obj.functions.balanceOf(self.clientAddress))
            # alldone = self.filter_set("BeginAveraging(string)", target_contract, self.handle_BeginAveraging_event)
        else:
            return "not me"

class DMLRunner(object):
    """
    DML Runner

    This class manages the training and validation of a DML job. It trains or
    validate a specified machine learning model on a local dataset. An instance
    of this class has a one-to-one relationship with a DML job, and gets freed up
    for another DML job after executing the job. Once free, it can schedule a new
    DML job from any DML session and repeat the cycle.

    Note that this class does not schedule how jobs received should be executed
    nor listens to incoming jobs. This class only executes the jobs.

    """

    def __init__(self, dataset_path, config):
        """
        Sets up the unique identifier of the DML Runner and the local dataset path.
        """
        self.iden = str(uuid.uuid4())[:8]
        self.dataset_path = dataset_path
        self.config = config
        self.data_count = count_datapoints(dataset_path)

    def train(self, serialized_model, model_type, initial_weights, hyperparams,
        labeler):
        """
        Trains the specified machine learning model on all the local data,
        starting from the initial model state specified, until a stopping
        condition is met, and using the hyper-parameters specified.

        Returns the updated model weights, the weighting factor omega, and stats
        about the training job.

        NOTE: Uses the same hyperparameters and labeler for training and
        validating during 'avg_type' of type 'val_acc'.
        """
        # Get the right dataset iterator based on the averaging type.
        avg_type = hyperparams['averaging_type']
        batch_size = hyperparams['batch_size']
        assert avg_type in ['data_size', 'val_acc'], \
            "Averaging type '{0}' is not supported.".format(avg_type)
        if avg_type == 'data_size':
            dataset_iterator = create_train_dataset_iterator(self.dataset_path, \
                count=self.data_count, split=self.config['split'], \
                batch_size=batch_size, labeler=labeler)
        elif avg_type == 'val_acc':
            dataset_iterator = create_train_dataset_iterator(self.dataset_path, \
                count=self.data_count, batch_size=batch_size, labeler=labeler)
            test_dataset_iterator = create_test_dataset_iterator(self.dataset_path, \
                count=self.data_count, split=self.config['split'], \
                batch_size=batch_size, labeler=labeler)

        # Train the model the right way based on the model type.
        assert model_type in ['keras'], \
            "Model type '{0}' is not supported.".format(model_type)
        if model_type == 'keras':
            new_weights, train_stats = train_keras_model(serialized_model,
                initial_weights, dataset_iterator, \
                self.data_count*self.config['split'], hyperparams)

        # Get the right omega based on the averaging type.
        if avg_type == 'data_size':
            omega = self.data_count * self.config['split']
        elif avg_type == 'val_acc':
            val_stats = self.validate(serialized_model, model_type, new_weights,
                hyperparams, labeler, custom_iterator=test_dataset_iterator)
            omega = val_stats['val_metric']['acc']
            train_stats.update(val_stats)

        # Return the results.
        return new_weights, omega, train_stats

    def validate(self, serialized_model, model_type, weights, hyperparams,
        labeler, custom_iterator=None):
        """
        Validates on all the local data the specified machine learning model at
        the state specified.

        Returns the metrics returned by the model.
        """
        # Choose the dataset to validate on.
        batch_size = hyperparams['batch_size']
        if custom_iterator is None:
            dataset_iterator = create_test_dataset_iterator(self.dataset_path, \
                count=self.data_count, split=(1-self.config['split']), \
                batch_size=batch_size, labeler=labeler)
        else:
            dataset_iterator = custom_iterator

        # Validate the model the right way based on the model type.
        assert model_type in ['keras'], \
            "Model type '{0}' is not supported.".format(model_type)
        if model_type == 'keras':
            val_stats = validate_keras_model(serialized_model, weights,
                dataset_iterator, self.data_count*(1-self.config['split']))

        # Return the validation stats.
        return val_stats

    def initialize_model(self, serialized_model, model_type):
        """
        Initializes and returns the model weights as specified in the model.
        """
        assert model_type in ['keras'], \
            "Model type '{0}' is not supported.".format(model_type)
        if model_type == 'keras':
            model = model_from_serialized(serialized_model)
            initial_weights = model.get_weights()
        return initial_weights


def train_keras_model(serialized_model, weights, dataset_iterator, data_count, hyperparams):
    logging.info('Keras training just started.')
    assert weights != None, "Initial weights must not be 'None'."
    model = model_from_serialized(serialized_model)
    model.set_weights(weights)
    hist = model.fit_generator(dataset_iterator, epochs=hyperparams['epochs'], \
        steps_per_epoch=data_count//hyperparams['batch_size'])
    new_weights = model.get_weights()
    logging.info('Keras training complete.')
    return new_weights, {'training_history' : hist.history}


def validate_keras_model(serialized_model, weights, dataset_iterator, data_count):
    logging.info('Keras validation just started.')
    assert weights != None, "weights must not be 'None'."
    model = model_from_serialized(serialized_model)
    model.set_weights(weights)
    history = model.evaluate_generator(dataset_iterator, steps=data_count)
    metrics = dict(zip(model.metrics_names, history))
    logging.info('Keras validation complete.')
    return {'val_metric': metrics}


if __name__ == '__main__':
    config = {
        'split': 0.8,
    }

    runner = DMLRunner('datasets/mnist', config)

    from models.keras_perceptron import KerasPerceptron
    m = KerasPerceptron(is_training=True)
    model_architecture = m.model.to_json()
    model_optimizer = get_optimizer(m.model)
    model_json = {
        "architecture": model_architecture,
        "optimizer": model_optimizer
    }
    print(model_json)

    initial_weights = runner.initialize_model(model_json, 'keras')

    hyperparams = {
        'averaging_type': 'data_size',
        'batch_size': 50,
        'epochs': 2,
    }

    from examples.labelers import mnist_labeler
    new_weights, omega, train_stats = runner.train(
        model_json,
        'keras',
        initial_weights,
        hyperparams,
        mnist_labeler
    )
    print(omega, train_stats)

    val_stats = runner.validate(
        model_json,
        'keras',
        new_weights,
        hyperparams,
        mnist_labeler
    )
    print(val_stats)
