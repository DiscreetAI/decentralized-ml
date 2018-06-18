import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from eth_utils import is_address
from blockchain_utils import *
from ipfs_utils import *

ETH_NODE_ADDR = 'http://54.153.84.146:8545'
TEMP_DELEGATOR_ADDR = '0x3b35797e426f6f92104f273b951af76c4a6484cb'
# TEMP_DELEGATOR_ADDR = self.web3.toChecksumAddress('0x9522f8d44ea66b96fcda5cb0c483759efa44adcd')
# TEMP_DELEGATOR_ABI = '''[{"constant":false,"inputs":[{"name":"_clientArray","type":"address[]"},{"name":"_modelAddrs","type":"bytes32[]"}],"name":"makeQuery","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"anonymous":false,"inputs":[{"indexed":false,"name":"clientArray","type":"address[]"},{"indexed":false,"name":"StateMachineAddress","type":"address"}],"name":"NewQuery","type":"event"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"}]'''
# TEMP_STATEMACHINE_ABI = '''[{"constant":false,"inputs":[],"name":"terminate","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_newModelAddrs","type":"bytes32[]"}],"name":"newModel","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_amt","type":"uint256"}],"name":"reward","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"stage","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"viewValidator","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[{"name":"_validator","type":"address"},{"name":"_listeners","type":"address[]"}],"payable":true,"stateMutability":"payable","type":"constructor"},{"anonymous":false,"inputs":[],"name":"NewModel","type":"event"},{"anonymous":false,"inputs":[],"name":"DoneTraining","type":"event"}]'''
TEMP_STATEMACHINE_ADDR = '0xefaee6745b40206efeb188cac3794a10c041198b'
# DML-Related Imports
# from dmljob import DMLJob
# from scheduler import Scheduler

from web3.auto import w3
from scheduler import DMLScheduler
from core.utils.dmljob import DMLJob

class ListenerEthereum(object):
    """
    This class listens to the deployed smart contract.
    """
    def __init__(self, clientAddress=None):

        # Connect scheduler
        # self.scheduler = DMLScheduler()
        self.web3 = Web3(HTTPProvider('http://54.153.84.146:8545'))        
        # Set up web3 and IPFS. MAKE SURE TO RUN 'IPFS DAEMON' BEFORE TRYING THIS!
        # self.web3 = Web3(IPCProvider())
        assert self.web3.isConnected()
        # self.api = ipfsapi.connect('127.0.0.1', 5001)
        
        # Set up the ETH account
        self.PASSPHRASE = 'panda'
        self.TEST_ACCOUNT = "0x1554a1d22cae251e2050f67cd3cf3082c4a784e6"

        if clientAddress:
            assert(is_address(clientAddress))
            self.clientAddress = clientAddress
        else:
            #TODO: Initialize client 'container' address if it wasn't assigned one
            self.clientAddress = self.TEST_ACCOUNT
        # self.web3.personal.unlockAccount(self.clientAddress, self.PASSPHRASE)
    
        print("Client Address:", self.clientAddress)

        # Start reading in the contracts
        # self.delegator = self.web3.eth.contract(
        #     address = TEMP_DELEGATOR_ADDR,
        #     abi = TEMP_DELEGATOR_ABI)

    async def start_listening(self, event_to_listen, poll_interval=5):
        while True:
            lst = event_to_listen.get_new_entries()
            if lst:
                print(lst[0])
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
            check = handler(inter['data'])
        finally:
            loop.close()
        return check

    def handle_newstatemachine(self, event_data):
        print(event_data)
        address = "".join(event_data.split("000000000000000000000000"))
        print(address)
        assert(is_address(address))
        self.listen_statemachine(address)
        return address

    def listen_delegator(self, event_data=None):
        self.filter_set(
            "NewQuery(address)",
            TEMP_DELEGATOR_ADDR, self.handle_newstatemachine)

    def listen_statemachine(self, address=TEMP_STATEMACHINE_ADDR):
        self.filter_set("NewModel(bytes32[])", address, self.handle_newmodel)
        # self.filter_set("DoneTraining()", address, self.checkBalance)

    def checkBalance(self, event_data):
        print(event_data)
        expectedBalance = event_data.split("000000000000000000000000")[2]
        myBalance = self.web3.eth.getBalance(self.clientAddress)
        assert myBalance == expectedBalance

    def handle_newmodel(self, event_data=None):
        print(event_data)
        try:
            model_addr = event_data.split("000000000000000000000000")[2]
            print("model_addr:{}".format(model_addr))
        except:
            model_addr = b'\xa8*\x06\xd4\x92\x8b\xfe\xa5\tX\x8d\x818\xc9"\xba\t^d\x1c\xe9\xc8R\x93:\xf2h\x8aX|\x9a\x1a'
        model_json = get_model(base322ipfs(model_addr))
        new_job = DMLJob(model_json)
        self.scheduler.add_job(new_job)
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