import logging
from threading import Event, Timer
import time
from typing import Callable, Tuple

import ipfsapi

from core.blockchain.blockchain_utils   import (filter_diffs, TxEnum,
                                                get_global_state, ipfs_to_content)
from core.utils.enums                   import RawEventTypes, MessageEventTypes


logging.basicConfig(level=logging.DEBUG,
    format='[BlockchainGateway] %(message)s')

class BlockchainGateway(object):
    """
    Blockchain Gateway 
    The blockchain gateway listens to the blockchain and notifies the appropriate classes
    inside the Unix Service when there is relevant information ready for them. Follows
    an event-driven programming paradigm using a series of async loops for listening.
    In order for this to work, the following must be running:
        IPFS Daemon: `ipfs daemon`
        The lotion app: `node app_trivial.js` from dagora-chain
    For more specific instructions check travis.yaml to see how travis does it.
    """

    def __init__(self):
        """
        Initialize state to an empty list. Everything else is left to configure().
        """
        self.state = []
        self.event = Event()

    def configure(self, config_manager: object, communication_manager: object):
        """
        Add communication_manager.
        Set up IPFS client via config_manager.
        """
        self.communication_manager = communication_manager
        config = config_manager.get_config()
        self.host = config.get("BLOCKCHAIN", "host")
        self.ipfs_port = config.getint("BLOCKCHAIN", "ipfs_port")
        self.port = config.getint("BLOCKCHAIN", "http_port")
        self.timeout = config.getint("BLOCKCHAIN", "timeout")
        try:
            self.client = ipfsapi.connect(self.host, self.ipfs_port)
        except Exception as e:
            logging.info("IPFS daemon not started, got: {0}".format(e))
            raise(e)

    # Public methods for CRON
    
    def start_cron(self, period_in_mins: float=0.05) -> None:
        """
        CRON method to listen. Runs asynchronously.
        """
        logging.info("Starting cron...")
        self._listen_as_event(
                        period_in_mins, 
                        self._handle_new_session_creation,
                        self._filter_new_session
        )
   
    def stop_cron(self) -> None:
        """
        Stop the CRON method.
        """
        self.event.set()
        logging.info("Cron stopped!")
  
    def reset(self) -> None:
        """
        Reset the gateway
        """
        self.event = Event()
        self.state = []
        logging.info("Gateway reset!")
    
    # Private methods to manage listening

    def _update_local_state(self, global_state_wrapper: dict) -> None:
        """
        Helper function to update the local state with freshly downloaded global state.
        """
        self.state = global_state_wrapper.get(TxEnum.MESSAGES.name, {})
    
    def _listen(self, callback: Callable, 
                event_filter: Callable) -> Tuple[Callable, Callable]:
        """
        Fetches the global state.
        Passes the global state to a filter to see all relevant transactions.
        Updates local state.
        If any relevant transactions found, returns the callback result.
        Else, returns the arguments it was passed.
        """
        global_state_wrapper = get_global_state(self.host, self.port, self.timeout)
        filtered_diffs = filter_diffs(global_state_wrapper, self.state, event_filter)
        self._update_local_state(global_state_wrapper)
        if filtered_diffs:
            return callback(filtered_diffs)
        else:
            return callback, event_filter
   
    def _listen_as_event(self, 
                        period_in_mins: float, 
                        callback: Callable, 
                        event_filter: Callable) -> None:
        """
        Trigger above method every period.
        """
        new_callback, event_filter = self._listen(callback, event_filter)
        if not self.event.is_set():
            Timer(
                period_in_mins * 60,
                self._listen_as_event,
                [period_in_mins, new_callback, event_filter]
            ).start()

    def _handle_new_session_creation(self, txs: list) -> Tuple[Callable, Callable]:
        """
        Maps the handler onto all relevant transactions.
        Then returns the next handler and filter.
        """
        def handler(tx):
            assert TxEnum.KEY.name in tx
            key = tx.get(TxEnum.KEY.name)
            value = tx.get(TxEnum.CONTENT.name)
            self.communication_manager.inform(RawEventTypes.NEW_SESSION.name, ipfs_to_content(self.client, value))
        list(map(handler, txs))
        return self._handle_new_session_info, self._filter_new_session_info
    
    def _filter_new_session(self, tx: dict) -> bool:
        """
        Only allows new-session transactions through.
        """
        return tx.get(TxEnum.KEY.name) == tx.get(TxEnum.CONTENT.name)
    
    def _filter_new_session_info(self, tx: dict) -> bool:
        """
        Only allows new-session-info transactions through.
        """
        return tx.get(TxEnum.KEY.name) != tx.get(TxEnum.CONTENT.name)
    
    def _handle_new_session_info(self, txs: list) -> Tuple[Callable, Callable]:
        """
        Maps the handler onto all relevant transactions.
        Then returns the next handler and filter.
        """
        def handler(tx):
            key = tx.get(TxEnum.KEY.name)
            value = tx.get(TxEnum.CONTENT.name)
            args = {TxEnum.KEY.name: MessageEventTypes.NEW_WEIGHTS.name, 
                    TxEnum.CONTENT.name: ipfs_to_content(self.client, value)}
            # TODO: Put into in-memory datastore.
            self.communication_manager.inform(
                RawEventTypes.NEW_INFO.name,args)
        list(map(handler, txs))
        return self._handle_new_session_info, self._filter_new_session_info
