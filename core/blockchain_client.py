"""
https://dagora.quip.com/HrXzAFdmLlIT/Model-Developer-Notebook

The DL2 Notebook needs to some kind of blockchain client that can make some kind of get an ED directory off the blockchain. In addition, the UNIX Service will need the client to be able to post ED directories on the blockchain. You can find more information on ED Directories  [here](https://dagora.quip.com/qnDPAFsMXfjN/Tech-Appendix).

Specifically, this is what needs to be done:

1. Create a new class called `BlockchainClient` (or whatever name you want) in the `decentralized_ml/core` repo with a method `post_dataset` that can post an ED Directory (JSON) with some kind of key (string). If there's any blockchain specific files you have, you might want to put them in the `blockchain` folder. You're free to change how the actual schema is (i.e. not a [key, value] pair).

2.  Create a new class called `BlockchainClient` (or whatever name you want) in the `dl-dl-notebook/core` repo with a method `get_dataset` can retrieve an ED Directory (JSON) with some kind of key (string). If there's any blockchain specific files you have, you might want to put them in a `blockchain` folder. Like above, you're free to change the schema if you want.

3. Modify the `DatasetManager` class so that `self.client` is an instance of the blockchain client and that `post_dataset`/`post_dataset_with_md` post the dataset as a key value pair.

4. Depending on what you have already, you may need to write tests for `BlockchainClient` (you can make the call).

5. When you're done, make a pull request to both repos and request me (and maybe Georgy) as a reviewer

Feel free to look at `client.py` to see how the [key,value] post worked. Might even be able to work off it? Also, feel free to break this down into multiple Trello cards (I just wanted to centralize all the information).

Message Neel on Slack if you have any questions! 
"""

class BlockchainClient(object):
    def __init__(self):
        # initialize
    def get_dataset(self, dataset):
        # post dataset to chain

"""
import os, inspect, sys
from eth_utils import is_address, to_checksum_address

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from core.blockchain.blockchain_utils import *
from core.blockchain.ipfs_utils import *

abi = '''[{"constant":false,"inputs":[{"name":"name","type":"string"}],"name":"getter","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"anonymous":false,"inputs":[{"indexed":false,"name":"addr","type":"bytes32"}],"name":"NewEntry","type":"event"},{"constant":false,"inputs":[{"name":"name","type":"string"},{"name":"addr","type":"bytes32"}],"name":"setter","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"constant":true,"inputs":[{"name":"","type":"bytes32"}],"name":"metaDb","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"}]'''
ALPHA_URL = 'http://54.153.84.146:8545'
ALPHA_ADDR = '0xb2CA9a58ea16599C2c827F399d07aA94b3C69dFb'
BETA_URL = 'http://18.144.49.201:8545'
BETA_ADDR = '0x0d65094fee55c21e256d52602a0dd6a23072223d'
GAMMA_URL = 'http://18.144.19.67:8545'
GAMMA_ADDR = '0x8f8301d2ac2294ad243ab7052054c3aa9a068965'

class Client(object):
	def __init__(self, nodeURL = None, nodeAddr = None):
		if nodeURL and nodeAddr:
			self.web3 = Web3(HTTPProvider(nodeURL))
			self.clientAddress = nodeAddr
		else:
			self.web3 = Web3(HTTPProvider(ALPHA_URL))
			self.clientAddress = ALPHA_ADDR
		assert self.web3.isConnected()
		# print(self.web3.personal.importRawKey('5b72313ec1c354bb06b909a8d5662452241396d62d730c72093ae053ac8bc9a0', 'boomboompow'))
		# self.api = ipfsapi.connect('127.0.0.1', 5001)
		CONTRACT_ADDRESS = to_checksum_address('0x39f3ba63142adf7455839fb4f91e7670a332a330')
		print(self.clientAddress)
		self.web3.personal.unlockAccount(self.clientAddress, 'panda')
		# compiled_sol = compile_files('Database.sol')
		# Database_id, Database_interface = compiled_sol.popitem()
		self.contract_obj = self.web3.eth.contract(address=CONTRACT_ADDRESS,
				   abi=abi)

	def setter(self, key, value):
		value = json2bytes32(value)
		tx_hash = self.contract_obj.functions.setter(key, value).transact({'from': self.clientAddress})
		self.web3.eth.waitForTransactionReceipt(tx_hash)
		tx_receipt = self.web3.eth.getTransactionReceipt(tx_hash)
		return tx_receipt

	def getter(self, key):
		tx_hash = self.contract_obj.functions.getter(key).transact({'from': self.clientAddress})
		self.web3.eth.waitForTransactionReceipt(tx_hash)
		tx_receipt = self.web3.eth.getTransactionReceipt(tx_hash)
		attr_dict = self.contract_obj.events.NewEntry().processReceipt(tx_receipt)
		print(attr_dict)
		addr = attr_dict[0]['args']['addr']
		print(addr)
		return bytes322json(addr)
if __name__ == '__main__':
	client = Client()
	client.setter("test", "test123")
	print(client.getter("test"))
    ##########################################################################
    ###                         DEVELOPER SECTION                          ###
    ##########################################################################

    def broadcast_decentralized_learning(self, model_config: object)-> str:
        """
        Upload a model config and weights to the blockchain
        """
        tx_receipt = setter(self.client, None, self.port, model_config, flag=True)
        return tx_receipt

    def broadcast_terminate(self, key: str) -> str:
        """
        Terminates decentralized training
        TODO: check if training even started
        """
        tx_receipt = setter(self.client, key, self.port, None)
        return tx_receipt

    def handle_decentralized_learning_owner(self, model_config: object) -> None:
        """
        Return weights after training terminates
        TODO: add condition to check if training for specific model terminated
        """
        final_weights = getter(self.client, model_config, self.state, self.port, self.timeout)
        return final_weights
"""
