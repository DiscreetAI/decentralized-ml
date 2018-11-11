import json
import logging
import requests
import time

import ipfsapi


logging.basicConfig(level=logging.DEBUG,
    format='[BlockchainClient] %(message)s')

class BlockchainClient(object):
    """
    In order for this to work, the following must be running:
        IPFS Daemon: `ipfs daemon`
        The lotion app: `node app_trivial.js` from dagora-chain
    """
    CONTENT = 'CONTENT'
    KEY = 'KEY'
    MESSAGES = 'MESSAGES'

    def __init__(self, config_filepath: str = 'blockchain_config.json') -> None:
        """
        Connect with running IPFS node.
        """
        with open(config_filepath) as f:
            config = json.load(f)
        self.host = config.get("host")
        self.ipfs_port = config.get("ipfs_port")
        self.port = config.get("http_port")
        self.timeout = config.get("timeout")
        self.client = None
        try:
            self.client = ipfsapi.connect(self.host, self.ipfs_port)
        except Exception as e:
            logging.info("IPFS daemon not started, got: {0}".format(e))
            raise e

    ## GETTER ##

    def _construct_getter_call(self) -> str:
        """
        Construct call to get state of running Lotion blockchain.
        """
        return "http://{0}:{1}/state".format(self.host, self.port)

    def _make_getter_call(self) -> object:
        """
        Make the call to get the state of the blockchain and raise status to
        preempt for errors.
        """
        tx_receipt = requests.get(self._construct_getter_call())
        tx_receipt.raise_for_status()
        return tx_receipt

    def _get_global_state(self) -> object:
        """
        Gets the global state which should be a list of dictionaries.
        """
        timeout = time.time() + self.timeout
        tx_receipt = None
        while time.time() < timeout:
            try:
                tx_receipt = self._make_getter_call().json()
                break
            except (UnboundLocalError, requests.exceptions.ConnectionError) as e:
                logging.info("HTTP GET error, got: {0}".format(e))
                continue
        return tx_receipt.get(BlockchainClient.MESSAGES)

    def get_dataset(self, key: str) -> object:
        """
        Stateless method to pull newest state from the blockchain and query it
        for the relevant key. Then pull the object with the corresponding key
        from IPFS. Assume that if there's a key match, only one element has
        matched.
        """
        filtered_state = list(filter(
            lambda tx: tx.get(BlockchainClient.KEY) == key,
            self._get_global_state()
          ))
        assert filtered_state
        ipfs_hash = filtered_state[0].get(BlockchainClient.CONTENT)
        return self.client.get_json(ipfs_hash)

    ## SETTER ##

    def _construct_setter_call(self) -> str:
        """
        Construct call to set to the running Lotion blockchain.
        """
        return "http://{0}:{1}/txs".format(self.host, self.port)

    def _make_setter_call(self, tx: dict) -> object:
        """
        Make the call to set content on the blockchain and raise status to
        preempt for errors.
        """
        tx_receipt = requests.post(self._construct_setter_call(), json=tx)
        tx_receipt.raise_for_status()
        return tx_receipt

    def post_dataset(self, key: str, value: object) -> str:
        """
        Provided a key and a JSON/np.array object, upload the object to IPFS and
        then store the hash as the value on the blockchain. The key should be a
        backward reference to a prior tx
        """
        ipfs_hash = self.client.add_json(value)
        tx = {BlockchainClient.KEY: key, BlockchainClient.CONTENT: ipfs_hash}
        timeout = time.time() + self.timeout
        tx_receipt = None
        while time.time() < timeout:
            try:
                tx_receipt = self._make_setter_call(tx)
                break
            except (UnboundLocalError, requests.exceptions.ConnectionError) as e:
                logging.info("HTTP SET error, got: {0}".format(e))
                continue
        return tx_receipt.text
