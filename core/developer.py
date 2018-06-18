import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from eth_utils import is_address
from blockchain.blockchain_utils import *
from blockchain.ipfs_utils import *

TEMP_DELEGATOR_ADDR = '0x009f87d4aab161dc5d5b67271b931dbc43d05cef'
TEMP_DELEGATOR_ABI = '''
[{"constant":false,"inputs":[{"name":"_clientArray","type":"address[]"},{"name":"_modelAddrs","type":"bytes32[2]"}],"name":"makeQuery","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"anonymous":false,"inputs":[{"indexed":false,"name":"addr","type":"address"},{"indexed":false,"name":"models","type":"bytes32[2]"},{"indexed":false,"name":"validator","type":"address"}],"name":"NewQuery","type":"event"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"}]
'''
TEMP_STATEMACHINE_ABI = '''
[{"constant":false,"inputs":[],"name":"terminate","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_newModelAddrs","type":"bytes32"}],"name":"newWeights","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[{"name":"_validator","type":"address"}],"payable":true,"stateMutability":"payable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"name":"addr","type":"bytes32"}],"name":"NewWeights","type":"event"},{"anonymous":false,"inputs":[],"name":"DoneTraining","type":"event"}]
'''
ALPHA_URL = 'http://54.153.84.146:8545'
ALPHA_ADDR = '0xb2CA9a58ea16599C2c827F399d07aA94b3C69dFb'
BETA_URL = 'http://18.144.49.201:8545'
BETA_ADDR = '0x0d65094fee55c21e256d52602a0dd6a23072223d'
GAMMA_URL = 'http://18.144.19.67:8545'
GAMMA_ADDR = '0x8f8301d2ac2294ad243ab7052054c3aa9a068965'
# TEMP_STATEMACHINE_ADDR = '0x2d3dbaa17e79c9ad964c88d2351d6157648de148'
# DML-Related Imports
# from dmljob import DMLJob
# from scheduler import Scheduler

from custom.keras import model_from_serialized, get_optimizer
from data.iterators import count_datapoints
from data.iterators import create_train_dataset_iterator
from data.iterators import create_test_dataset_iterator
from core.utils.keras import train_keras_model, validate_keras_model

from web3.auto import w3

class DMLDeveloper(object):
    """
    This class creates StateMachine smart contracts to train models.
    """
    def __init__(self, clientAddress=None):

        if clientAddress:
            self.web3 = Web3(IPCProvider())
            assert self.web3.isConnected()
            self.clientAddress = clientAddress
            # self.clientAddress = self.web3.toChecksumAddress(clientAddress)
        else:
            self.web3 = Web3(HTTPProvider(BETA_URL))
            assert self.web3.isConnected()
            self.clientAddress = self.web3.toChecksumAddress(BETA_ADDR)
            self.web3.personal.unlockAccount(self.clientAddress, 'panda')
        # self.api = ipfsapi.connect('127.0.0.1', 5001)
        

        # Start reading in the contracts
        self.delegator = self.web3.eth.contract(
            address = self.web3.toChecksumAddress(TEMP_DELEGATOR_ADDR),
            abi = TEMP_DELEGATOR_ABI)
    
    def deploy_with_model(self, model, model_json):
        weights_bytes = weights2bytes32(model)   
        complete_json = {'serialized_model' : model_json,
                'job_type' : 'initialize',
                'model_type' : 'keras'}
        json_bytes = json2bytes32(complete_json)
        return self.deploy_StateMachine([self.clientAddress], [json_bytes, weights_bytes])

    def deploy_StateMachine(self, targetAddrs, modelAddrsBytes):
        print(targetAddrs)
        print(modelAddrsBytes)

        # Deploy StateMachine

        tx_hash = self.delegator.functions.makeQuery(
            targetAddrs, modelAddrsBytes).transact({'from': self.clientAddress})

        # Parse the output

        self.web3.eth.waitForTransactionReceipt(tx_hash)
        tx_receipt = self.web3.eth.getTransactionReceipt(tx_hash)
        self.web3.personal.lockAccount(self.clientAddress)
        attr_dict = self.delegator.events.NewQuery().processReceipt(tx_receipt)
        print(attr_dict)
        addr = attr_dict[0]['args']['addr']
        print(addr)
        # Read in the new StateMachine

        self.stateMachine = self.web3.eth.contract(
            address = self.web3.toChecksumAddress(addr),
            abi = TEMP_STATEMACHINE_ABI)
    def terminate(self):
        '''
        Terminates decentralized training.
        '''
        tx_hash = self.stateMachine.functions.terminate().transact({'from': self.clientAddress})
        self.web3.eth.waitForTransactionReceipt(tx_hash)
        tx_receipt = self.web3.eth.getTransactionReceipt(tx_hash)
        attr_dict = self.stateMachine.events.DoneTraining().processReceipt(tx_receipt)
        print(attr_dict)
        
    def update_weights(self, model):
        '''
        Takes in a model.
        Extracts the weights from the model and puts them into a file.
        Puts it on IPFS and returns the Bytes32 of the IPFSHash.
        Calls update_StateMachine() with this new argument.
        '''
        self.update_StateMachine(weights2bytes32(model))

    def update_StateMachine(self, weightsAddrBytes):
        '''
        Takes in the Bytes32 referencing an IPFS Hash of a model weights file.
        Updates StateMachine with its argument. 
        Asserts that the updated value in StateMachine is equal to its input.
        '''
        print(weightsAddrBytes)
        tx_hash = self.stateMachine.functions.newWeights(weightsBytes).transact({'from': self.clientAddress})
        self.web3.eth.waitForTransactionReceipt(tx_hash)
        tx_receipt = self.web3.eth.getTransactionReceipt(tx_hash)
        attr_dict = self.stateMachine.events.NewWeights().processReceipt(tx_receipt)
        print(attr_dict)
        addr = attr_dict[0]['args']['addr']
        print(addr)
        assert weightAddrsBytes == addr

    # def upload_model(model_json, model_weights):

    # async def start_listening(self, event_to_listen, poll_interval=5):
    #     while True:
    #         lst = event_to_listen.get_new_entries()
    #         if lst:
    #             # print(lst[0])
    #             return lst[0]
    #         await asyncio.sleep(poll_interval)

    # def filter_set(self, event_sig, contract_addr, handler):
    #     print(contract_addr)
    #     event_signature_hash = self.web3.sha3(text=event_sig).hex()
    #     event_filter = self.web3.eth.filter({
    #         "address": contract_addr.lower(),
    #         "topics": [event_signature_hash]
    #         })
    #     asyncio.set_event_loop(asyncio.new_event_loop())
    #     loop = asyncio.get_event_loop()
    #     try:
    #         inter = loop.run_until_complete(
    #             self.start_listening(event_filter, 2))
    #         check = handler(inter['data'])
    #     finally:
    #         loop.close()
    #     return check

    # def handle_newstatemachine(self, event_data):
    #     print(event_data)
    #     address = event_data.split("000000000000000000000000")[2]
    #     assert(is_address(address))
    #     self.listen_statemachine(address)
    #     return event_data.split("000000000000000000000000")

    # def listen_delegator(self, event_data=None):
    #     self.filter_set(
    #         "NewQuery(address[] clientArray, address StateMachineAddress)",
    #         TEMP_DELEGATOR_ADDR, self.handle_newstatemachine)

    # def listen_statemachine(self, address=TEMP_STATEMACHINE_ADDR):
    #     self.filter_set("NewModel(bytes32)", address, self.handle_newmodel)
    #     # self.filter_set("DoneTraining()", address, self.checkBalance)

    # def checkBalance(self, event_data):
    #     print(event_data)
    #     expectedBalance = event_data.split("000000000000000000000000")[2]
    #     myBalance = self.web3.eth.getBalance(self.clientAddress)
    #     assert myBalance == expectedBalance

    # def handle_newmodel(self, event_data=None):
    #     # print(event_data)
    #     try:
    #         model_addr = event_data.split("000000000000000000000000")[2]
    #     except:
    #         model_addr = b'\xa8*\x06\xd4\x92\x8b\xfe\xa5\tX\x8d\x818\xc9"\xba\t^d\x1c\xe9\xc8R\x93:\xf2h\x8aX|\x9a\x1a'
    #     model_json = get_model(base322ipfs(model_addr))
    #     new_job = DMLJob(model_json)
    #     self.scheduler.enqueue(new_job)
    #     # return event_data.split("000000000000000000000000")

    # def main(self):
    #     # print(self.web3.eth.getBlock('latest'))
    #     # self.handle_newmodel()
    #     # check = self.filter_set("QueryCreated(address,address)", self.Delegator_address, self.handle_QueryCreated_event)
    #     # if check[0] + check[1] == self.clientAddress.lower():
    #     #     target_contract = check[0] + check[2]
    #     #     # print(target_contract)
    #     #     # retval = self.filter_set("ClientSelected(address,string)", target_contract, self.handle_ClientSelected_event)
    #     #     self.filter_set("ClientSelected(address,string)", target_contract, self.handle_ClientSelected_event)
    #     #     # return "I got chosen:", retval[0] + retval[1]
    #     #     # print("listening for next round to begin...")
    #     #     print("receiving reward...")
    #     #     contract_obj = self.web3.eth.contract(
    #     #     address=self.DAgoraToken_address,
    #     #     abi=self.DAgoraToken_interface['abi'])

    #     #     tx_hash = contract_obj.functions.transfer(self.clientAddress, 50000000).transact({'from': '0xf6419f5c5295a70C702aC21aF0f64Be07B59F3c4'})
    #     #     self.web3.eth.waitForTransactionReceipt(tx_hash)
    #     #     print('sent!')
    #     #     # print('Token Balance:', contract_obj.functions.balanceOf(self.clientAddress))
    #     #     # alldone = self.filter_set("BeginAveraging(string)", target_contract, self.handle_BeginAveraging_event)
    #     # else:
    #     #     return "not me"

if __name__ == '__main__':
    from models.keras_perceptron import KerasPerceptron
    m = KerasPerceptron(is_training=True)
    model_architecture = m.model.to_json()
    model_optimizer = get_optimizer(m.model)
    model_json = {
        "architecture": model_architecture,
        "optimizer": model_optimizer
    }
    developer = DMLDeveloper()
    developer.deploy_with_model(m.model, model_json)
