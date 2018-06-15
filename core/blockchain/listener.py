from eth_utils import is_address
from blockchain_utils import *
import ipfsapi

ETH_NODE_ADDR = 'http://54.153.84.146:8545'
TEMP_DELEGATOR_ADDR = '0x9522f8d44ea66b96fcda5cb0c483759efa44adcd'
# TEMP_DELEGATOR_ADDR = self.web3.toChecksumAddress('0x9522f8d44ea66b96fcda5cb0c483759efa44adcd')
# TEMP_DELEGATOR_ABI = '''[{"constant":false,"inputs":[{"name":"_clientArray","type":"address[]"},{"name":"_modelAddrs","type":"bytes32[]"}],"name":"makeQuery","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"anonymous":false,"inputs":[{"indexed":false,"name":"clientArray","type":"address[]"},{"indexed":false,"name":"StateMachineAddress","type":"address"}],"name":"NewQuery","type":"event"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"}]'''
# TEMP_STATEMACHINE_ABI = '''[{"constant":false,"inputs":[],"name":"terminate","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_newModelAddrs","type":"bytes32[]"}],"name":"newModel","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_amt","type":"uint256"}],"name":"reward","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"stage","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"viewValidator","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[{"name":"_validator","type":"address"},{"name":"_listeners","type":"address[]"}],"payable":true,"stateMutability":"payable","type":"constructor"},{"anonymous":false,"inputs":[],"name":"NewModel","type":"event"},{"anonymous":false,"inputs":[],"name":"DoneTraining","type":"event"}]'''

# DML-Related Imports
from dmljob import DMLJob
from scheduler import Scheduler

class ListenerEthereum(object):
    """
    This class listens to the deployed smart contract.
    """
    def __init__(self, clientAddress=None):

        # Connect scheduler
        self.scheduler = Scheduler()

        # Set up web3 and IPFS. MAKE SURE TO RUN 'IPFS DAEMON' BEFORE TRYING THIS!
        self.web3 = Web3(HTTPProvider(ETH_NODE_ADDR))
        assert self.web3.isConnected()
        self.api = ipfsapi.connect('127.0.0.1', 5001)
        
        # Set up the ETH account
        self.PASSPHRASE = 'panda'
        self.TEST_ACCOUNT = '0xf6419f5c5295a70C702aC21aF0f64Be07B59F3c4'

        if clientAddress:
            assert(is_address(clientAddress))
            self.clientAddress = clientAddress
        else:
            #TODO: Initialize client 'container' address if it wasn't assigned one
            self.clientAddress = self.TEST_ACCOUNT
        self.web3.personal.unlockAccount(self.clientAddress, self.PASSPHRASE)
    
        print("Client Address:", self.clientAddress)

        # Start reading in the contracts
        # self.delegator = self.web3.eth.contract(
        #     address = TEMP_DELEGATOR_ADDR,
        #     abi = TEMP_DELEGATOR_ABI)

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

    def handle_newstatemachine(self, event_data):
        print(event_data)
        address = event_data.split("000000000000000000000000")[2]
        assert(is_address(address))
        self.listen_statemachine(address)
        return event_data.split("000000000000000000000000")

    def listen_delegator(self, event_data=None):
        self.filter_set(
            "NewQuery(address[] clientArray, address StateMachineAddress)",
            TEMP_DELEGATOR_ADDR, self.handle_newstatemachine)

    def listen_statemachine(self, address):
        self.filter_set("NewModel()", address, self.handle_newmodel)
        self.filter_set("DoneTraining()", address, self.checkBalance)

    def checkBalance(self, event_data):
        print(event_data)
        expectedBalance = event_data.split("000000000000000000000000")[2]
        myBalance = self.web3.eth.getBalance(self.clientAddress)
        assert myBalance == expectedBalance

    def handle_newmodel(self, event_data):
        print(event_data)
        model_array = event_data.split("000000000000000000000000")[2]
        new_job = DMLJob(model_array)
        self.scheduler.enqueue(new_job)
        return event_data.split("000000000000000000000000")

    def main(self):
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