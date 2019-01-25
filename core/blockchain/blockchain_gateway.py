import logging
from threading import Event, Timer
import time
from typing import Callable, Tuple
from multiprocessing import Manager

import ipfsapi

from core.blockchain.blockchain_utils   import (filter_diffs, get_global_state,
                                                ipfs_to_content, Transaction, TxEnum)
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
        Initialize state, keys to empty lists. Everything else is left to configure().
        """
        self.state = Manager().list()
        self.event = Event()
        self.keys = []

    def configure(self, config_manager: object, communication_manager: object, 
                    ipfs_client: object, dataset_manager: object):
        """
        Add communication_manager, ipfs_client, and set port.
        """
        self.communication_manager = communication_manager
        self._dataset_manager = dataset_manager
        config = config_manager.get_config()
        self._host = config.get("BLOCKCHAIN", "host")
        self._port = config.getint("BLOCKCHAIN", "http_port")
        self._timeout = config.getint("BLOCKCHAIN", "timeout")
        self._client = ipfs_client

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
        This causes the Scheduler/Runners to no longer influence the Gateway's state
        """
        self.event = Event()
        self.state = Manager().list()
        logging.info("Gateway reset!")

    def state_append(self, set_element):
        """
        Called by other Setter methods used in the rest of the service.
        Making sure that the service doesn't pick up weights that were
        already generated.
        """
        logging.info("appending to state: {}".format(set_element))
        self.state.append(set_element)
    # Private methods to manage listening

    def _update_local_state(self, filtered_diffs: list) -> None:
        """
        Helper function to update the local state with freshly downloaded global state.
        """
        self.state.extend(filtered_diffs)
    
    def _listen(self, callback: Callable, 
                event_filter: Callable) -> Tuple[Callable, Callable]:
        """
        Fetches the global state.
        Passes the global state to a filter to see all relevant transactions.
        Updates local state.
        If any relevant transactions found, returns the callback result.
        Else, returns the arguments it was passed.
        """
        global_state_wrapper = get_global_state(self._host, self._port, self._timeout)
        state_diffs, filtered_diffs = filter_diffs(global_state_wrapper, self.state, event_filter)
        # return filtered_diffs
        self._update_local_state(state_diffs)
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
            args = Transaction(MessageEventTypes.NEW_SESSION.name,
                                Transaction(ipfs_to_content(self._client, key),
                                            ipfs_to_content(self._client, value), 0).get_tx(),
                                0).get_tx()
            self.communication_manager.inform(RawEventTypes.NEW_MESSAGE.name, args)
        list(map(handler, txs))
        return self._handle_new_session_info, self._filter_new_session_info

    def _filter_new_session(self, tx: dict) -> bool:
        """
        Only allows new-session transactions through.
        """
        try:
            key_dict = ipfs_to_content(self._client, tx.get(TxEnum.KEY.name))
            return self._dataset_manager.validate_key(key_dict["dataset_uuid"]) and tx.get(TxEnum.ROUND.name) == 0
        except:
            return False

    def _filter_new_session_info(self, tx: dict) -> bool:
        """
        Only allows new-session-info transactions through.
        """
        return tx.get(TxEnum.ROUND.name) > 0

    def _handle_new_session_info(self, txs: list) -> Tuple[Callable, Callable]:
        """
        Maps the handler onto all relevant transactions.
        Then returns the next handler and filter.
        """
        def handler(tx):
            key = tx.get(TxEnum.KEY.name)
            value = tx.get(TxEnum.CONTENT.name)
            args = Transaction(MessageEventTypes.NEW_WEIGHTS.name,
                                ipfs_to_content(self._client, value), 0).get_tx()
            # TODO: Put into in-memory datastore.
            self.communication_manager.inform(
                RawEventTypes.NEW_MESSAGE.name,args)
        list(map(handler, txs))
        return self._handle_new_session_info, self._filter_new_session_info
