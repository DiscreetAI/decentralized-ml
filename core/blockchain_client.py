import json
import logging
import requests
import time
from enum import Enum

import ipfsapi


logging.basicConfig(level=logging.DEBUG,
    format='[BlockchainClient] %(message)s')

class BlockchainClient(object):
    """
    In order for this to work, the following must be running:
        IPFS Daemon: `ipfs daemon`
        The lotion app: `node app_trivial.js` from dagora-chain
    """

    def __init__(self, config: object) -> None:
        """
        Connect with running IPFS node.
        """
        self.host = config.get("BLOCKCHAIN_CLIENT", "host")
        self.ipfs_port = config.getint("BLOCKCHAIN_CLIENT", "ipfs_port")
        self.port = config.getint("BLOCKCHAIN_CLIENT", "http_port")
        self.timeout = config.getint("BLOCKCHAIN_CLIENT", "timeout")

        self.client = None
        try:
            self.client = ipfsapi.connect(self.host, self.ipfs_port)
        except Exception as e:
            logging.info("IPFS daemon not started, got: {0}".format(e))
            raise e

    ## GETTER ##
    def _ipfs_to_content(self, client: object, ipfs_hash: str) -> object:
        """
        Helper function to retrieve a Python object from an IPFS hash
        """
        return client.get_json(ipfs_hash)
    
    def _construct_getter_call(self, host: str, port: int) -> str:
        return "http://{0}:{1}/state".format(host, port)

    def _make_getter_call(self, host: str, port: int) -> object:
        tx_receipt = requests.get(self._construct_getter_call(host, port))
        tx_receipt.raise_for_status()
        return tx_receipt

    def _get_global_state(self, host: str, port: int, timeout: int) -> object:
        """
        Gets the global state which should be a list of dictionaries
        TODO: perhaps it might be better to offload the retrying to the `getter`
        """
        timeout = time.time() + timeout
        tx_receipt = None
        while time.time() < timeout:
            try:
                tx_receipt = self._make_getter_call(host, port).json()
                break
            except (UnboundLocalError, requests.exceptions.ConnectionError) as e:
                logging.info("HTTP GET error, got: {0}".format(e))
                continue
        return tx_receipt

    def get_dataset(self, key: str) -> object:
        """
        Stateless method to pull newest state from the blockchain and query it
        for the relevant key. Then pull the object with the corresponding key
        from IPFS. Assume that if there's a key match, only one element has
        matched.
        """
        state = self._get_global_state(self.host, self.port, self.timeout)
        state = state.get(TxEnum.MESSAGES.name, {})
        relevant_txs = list(
            map(lambda tx: self._ipfs_to_content(self.client, tx.get(TxEnum.CONTENT.name)),
                filter(lambda tx: tx.get(TxEnum.KEY.name) == key, state)))
        assert relevant_txs, "No such key"
        return relevant_txs[0]

    ## SETTER ##
    def _upload(self, client: object, value: dict) -> str:
        """
        Provided any Python object, store it on IPFS and then upload the hash that
        will be uploaded to the blockchain as a value
        """
        # assert TxEnum.KEY.name in value
        # assert TxEnum.CONTENT.name in value
        ipfs_hash = self._content_to_ipfs(client, value)
        return str(ipfs_hash)
    
    def _content_to_ipfs(self, client: object, content: dict) -> str:
        """
        Helper function to deploy a Python object onto IPFS, returns an IPFS hash
        """
        return client.add_json(content)
    
    def _construct_setter_call(self, host: str, port: int) -> str:
        return "http://{0}:{1}/txs".format(host, port)

    def _make_setter_call(self, host: str, port: int, tx: dict) -> object:
        tx_receipt = requests.post(self._construct_setter_call(host, port), json=tx)
        tx_receipt.raise_for_status()
        return tx_receipt

    def post_dataset(self, key: str, value: object) -> str:
        """
        Provided a key and a JSON/np.array object, upload the object to IPFS and
        then store the hash as the value on the blockchain. The key should be a
        backward reference to a prior tx
        """
        on_chain_value = self._upload(self.client, value)
        tx = Transaction(key, on_chain_value, round_num=0)
        timeout = time.time() + self.timeout
        tx_receipt = None
        while time.time() < timeout:
            try:
                tx_receipt = self._make_setter_call(self.host, self.port, tx.get_tx())
                break
            except (UnboundLocalError, requests.exceptions.ConnectionError) as e:
                logging.info("HTTP SET error, got: {0}".format(e))
                continue
        return tx_receipt.text

##############################################################################
###                              OBJECTS                                   ###
##############################################################################

class TxEnum(Enum):
    """
    Enum of tx-related constants, e.g. standard keys present in a transaction
    """
    KEY = "KEY"
    CONTENT = "CONTENT"
    ROUND = "ROUND"
    MESSAGES = "MESSAGES"

class Transaction(object):
    """
    Object that represents transactions with the specification outlined:
        `{
            'key': ...
            'content': ...
         }`
    """
    def __init__(self, key: str, content: str, round_num: int) -> None:
        self.key = key
        self.content = content
        self.round_num = round_num

    def get_tx(self) -> dict:
       return {TxEnum.KEY.name: self.key, TxEnum.CONTENT.name: self.content,
                TxEnum.ROUND.name: self.round_num}
