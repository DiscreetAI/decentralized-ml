import asyncio
import time
import pprint
import requests
import pandas as pd

import rlp
import web3

from eth_utils import is_address
from ethereum.transactions import Transaction
from solc import compile_source, compile_files
from web3 import Web3, HTTPProvider, eth, IPCProvider
from web3.auto import w3
from web3.utils.events import get_event_data


def get_testnet_eth(w3, to_address, provider=None):
	TEST_ACCOUNT = '0xf6419f5c5295a70C702aC21aF0f64Be07B59F3c4'
	# tx = Transaction(
	# 	nonce=web3.eth.getTransactionCount(web3.eth.coinbase),
	# 	gasprice=web3.eth.gasPrice,
	# 	startgas=100000,
	# 	to=to_address,
	# 	value=99999999999,
	# 	data=b'')
	# tx.sign('146396092a127e4cf6ff3872be35d49228c7dc297cf34da5a0808f29cf307da1')
	# raw_tx = rlp.encode(tx)
	# raw_tx_hex = web3.toHex(raw_tx)
	# web3.eth.sendRawTransaction(raw_tx_hex)
	# ==============
	# web3.personal.Personal.importRawKey(
	# w3, private_key='146396092a127e4cf6ff3872be35d49228c7dc297cf34da5a0808f29cf307da1',passphrase='panda')
	web3.personal.Personal.unlockAccount(w3, TEST_ACCOUNT, 'panda')
	# print(w3.web3.eth.getBalance(TEST_ACCOUNT))
	if True:
		# tx = provider.eth.sendTransaction({"from": provider.eth.coinbase, "to": to_address, "value": 8535606699990000})
		tx = provider.eth.sendTransaction({"from": TEST_ACCOUNT, "to": to_address, "value": 8535606699990000})
		w3.web3.eth.waitForTransactionReceipt(tx)
	else:
		to_whom = '{"toWhom":"%s"}' % to_address
		url = 'https://ropsten.faucet.b9lab.com/tap'
		requests.post(url, data=to_whom)
		time.sleep(60)

def send_raw_tx(w3, to_address, from_address, from_key):
	tx = Transaction(
		nonce=0,
		gasprice=w3.eth.gasPrice,
		startgas=100000,
		to=to_address,
		value=12345,
		data=b''
	)

	tx.sign(from_key)
	raw_tx = rlp.encode(tx)
	raw_tx_hex = w3.toHex(raw_tx)
	w3.eth.sendRawTransaction(raw_tx_hex)

def compile_source_file(file_path):
	with open(file_path, 'r') as f:
		source = f.read()

	return compile_source(source)




def deploy_Query(w3, contract_interface, account, target_accounts):
	tx_hash = w3.eth.contract(
		abi=contract_interface['abi'],
		bytecode=contract_interface['bin']).constructor(1, 1, target_accounts).transact({"from": account})

	address = w3.eth.getTransactionReceipt(tx_hash)['contractAddress']
	return address

def deploy_Master(w3, contract_interface, account):
	tx_hash = w3.eth.contract(
		abi=contract_interface['abi'],
		bytecode=contract_interface['bin']).constructor().transact({"from": account})

	w3.eth.waitForTransactionReceipt(tx_hash)

	address = w3.eth.getTransactionReceipt(tx_hash)['contractAddress']
	return address




def wait_for_receipt(w3, tx_hash, poll_interval):
	while True:
		tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
		if tx_receipt:
			return tx_receipt
		time.sleep(poll_interval)

def txn_digest(txn):
	return "Contract address: {0}\nEvent: {1}\nArg: {2}".format(
		txn['address'], txn['event'], txn['args'])

def event_callback(arg):
	print(txn_digest(arg))

def wait_on_tx_receipt(tx_hash):
	start_time = time.time()
	while True:
		if start_time + 60 < time.time():
			raise TimeoutError("Timeout occurred waiting for tx receipt")
		if w3.eth.getTransactionReceipt(tx_hash):
			return w3.eth.getTransactionReceipt(tx_hash)

def deploy_contract(w3, contract_interface):
	tx_hash = w3.eth.contract(
		abi=contract_interface['abi'],
		bytecode=contract_interface['bin']).constructor().transact({"from": acct})

	address = w3.eth.getTransactionReceipt(tx_hash)['contractAddress']
	return address

def get_contract_address(address_name, db):
    try:
	    sample_data = pd.read_sql_query("select * from {}".format(address_name), db.engine)
	    return sample_data.to_json()
    except: 
        print('No contract address by the name of {} exists'.format(address_name))

def post_contract_address(contract_address, json, address_name, db):
    sample_data = pd.DataFrame()
    sample_data['contract_address'] = [contract_address]
    sample_data['json'] = [json]
    sample_data.to_sql(name=address_name, con=db.engine, if_exists='replace', index=False)
