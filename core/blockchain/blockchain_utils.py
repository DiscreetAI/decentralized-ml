import asyncio
import time
import pprint
import requests
import pandas as pd
import json

import rlp
import web3

from eth_utils import is_address
from ethereum.transactions import Transaction
from solc import compile_source, compile_files
from web3 import Web3, HTTPProvider, eth, IPCProvider
from web3.auto import w3
from web3.utils.events import get_event_data
from eth_abi import decode_abi

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

def decode_event(abi, event_data):
	input_dict = json.loads(abi)
	e = [x for x in input_dict if x['type'] == 'event'][0]
	types = [i['type'] for i in e['inputs']]
	names = [i['name'] for i in e['inputs']]
	values = decode_abi(types, bytearray.fromhex(event_data['data'][2:]))
	return dict(zip(names, values))

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
