import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from eth_utils import is_address
from blockchain_utils import *
from ipfs_utils import *

ETH_NODE_ADDR = 'http://54.153.84.146:8545'
TEMP_DELEGATOR_ADDR = '0x009f87d4aab161dc5d5b67271b931dbc43d05cef'
TEMP_DELEGATOR_ABI = '''
[{"constant":false,"inputs":[{"name":"_clientArray","type":"address[]"},{"name":"_modelAddrs","type":"bytes32[2]"}],"name":"makeQuery","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"anonymous":false,"inputs":[{"indexed":false,"name":"addr","type":"address"},{"indexed":false,"name":"models","type":"bytes32[2]"},{"indexed":false,"name":"validator","type":"address"}],"name":"NewQuery","type":"event"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"}]
'''
TEMP_STATEMACHINE_ABI = '''
[{"constant":false,"inputs":[],"name":"terminate","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_newModelAddrs","type":"bytes32"}],"name":"newWeights","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[{"name":"_validator","type":"address"}],"payable":true,"stateMutability":"payable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"name":"addr","type":"bytes32"}],"name":"NewWeights","type":"event"},{"anonymous":false,"inputs":[],"name":"DoneTraining","type":"event"}]
'''
# DML-Related Imports
# from dmljob import DMLJob
# from scheduler import Scheduler

from web3.auto import w3
from scheduler import DMLScheduler
from core.utils.dmljob import DMLJob
from core.runner import DMLRunner

class ListenerEthereum(object):
    """
    This class listens to the deployed smart contract.
    """
    def __init__(self, clientAddress=None):

        # Connect scheduler
        # self.scheduler = DMLScheduler()
        self.web3 = Web3(HTTPProvider(ETH_NODE_ADDR))      
        # Set up web3 and IPFS. MAKE SURE TO RUN 'IPFS DAEMON' BEFORE TRYING THIS!
        # self.web3 = Web3(IPCProvider())
        assert self.web3.isConnected()
        config = {}

        self.runner = DMLRunner('datasets/mnist', config)
        # self.api = ipfsapi.connect('127.0.0.1', 5001)
        
        # # Set up the ETH account
        # self.PASSPHRASE = 'panda'
        # self.TEST_ACCOUNT = "0x1554a1d22cae251e2050f67cd3cf3082c4a784e6"

        # if clientAddress:
        #     assert(is_address(clientAddress))
        #     self.clientAddress = clientAddress
        # else:
        #     #TODO: Initialize client 'container' address if it wasn't assigned one
        #     self.clientAddress = self.TEST_ACCOUNT
        # # self.web3.personal.unlockAccount(self.clientAddress, self.PASSPHRASE)
    
        # print("Client Address:", self.clientAddress)

        # Start reading in the contracts
        # self.delegator = self.web3.eth.contract(
        #     address = TEMP_DELEGATOR_ADDR,
        #     abi = TEMP_DELEGATOR_ABI)

    async def start_listening(self, event_to_listen, poll_interval=5):
        while True:
            lst = event_to_listen.get_new_entries()
            if lst:
                # print(lst[0])
                return lst[0]
            await asyncio.sleep(poll_interval)

    def filter_set(self, event_sig, contract_addr, handler):
        print(contract_addr)
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
            check = handler(inter)
        finally:
            loop.close()
        return check

    def handle_newstatemachine(self, event_data):
        event_json = decode_event(TEMP_DELEGATOR_ABI, event_data)
        stateMachineAddress = event_json['addr']
        print(stateMachineAddress)
        models = event_json['models']
        model_json = bytes322json(models[0])
        new_job = DMLJob(model_json)
        self.runner.run_job(new_job)
        # serialized_model = model_json['serialized_model']
        # model_weights = bytes322weights(serialized_model, models[1])
        # print(models)
        validator = event_json['validator']
        # print(event_json)
        self.listen_statemachine(stateMachineAddress)

    def listen_delegator(self, event_data=None):
        self.filter_set(
            "NewQuery(address,bytes32[2],address)",
            TEMP_DELEGATOR_ADDR, self.handle_newstatemachine)

    def listen_statemachine(self, address):
        self.filter_set("NewWeights(bytes32)", address, self.handle_newWeights)
        # self.filter_set("DoneTraining()", address, self.checkBalance)

    def checkBalance(self, event_data):
        print(event_data)
        expectedBalance = event_data.split("000000000000000000000000")[2]
        myBalance = self.web3.eth.getBalance(self.clientAddress)
        assert myBalance == expectedBalance

    def handle_newWeights(self, event_data=None):
        event_json = decode_event(TEMP_STATEMACHINE_ABI, event_data)
        model_addr_bytes = event_json['addr']
        model = bytes322weights(model_addr_bytes)
        # model = 
        # model_weights = get_model(base322ipfs(model_addr))
        # new_job = DMLJob(model_json)
        # self.scheduler.add_job(new_job)
        # return event_data.split("000000000000000000000000")

    def main(self):
        # print(self.web3.eth.getBlock('latest'))
        self.listen_delegator()
        # check = self.filter_set("QueryCreated(address,address)", self.Delegator_address, self.handle_QueryCreated_event)
        # if check[0] + check[1] == self.clientAddress.lower():
        #     target_contract = check[0] + check[2]
        #     # print(target_contract)
        #     # retval = self.filter_set("ClientSelected(address,string)", target_contract, self.handle_ClientSelected_event)
        #     self.filter_set("ClientSelected(address,string)", target_contract, self.handle_ClientSelected_event)
        #     # return "I got chosen:", retval[0] + retval[1]
        #     # print("listening for next round to begin...")
        #     print("receiving reward...")
        #     contract_obj = self.web3.eth.contract(
        #     address=self.DAgoraToken_address,
        #     abi=self.DAgoraToken_interface['abi'])

        #     tx_hash = contract_obj.functions.transfer(self.clientAddress, 50000000).transact({'from': '0xf6419f5c5295a70C702aC21aF0f64Be07B59F3c4'})
        #     self.web3.eth.waitForTransactionReceipt(tx_hash)
        #     print('sent!')
        #     # print('Token Balance:', contract_obj.functions.balanceOf(self.clientAddress))
        #     # alldone = self.filter_set("BeginAveraging(string)", target_contract, self.handle_BeginAveraging_event)
        # else:
        #     return "not me"

if __name__ == '__main__':
    listener = ListenerEthereum()
    listener.main()