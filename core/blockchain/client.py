import os
from blockchain_utils import *
from ipfs_utils import *
from eth_utils import is_address, to_checksum_address

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