import json
import logging
import requests
import time
import uuid

import ipfsapi

from core.blockchain_client import BlockchainClient, TxEnum, Transaction


logging.basicConfig(level=logging.DEBUG,
    format='[DMLClient] %(message)s')

class DMLClient(BlockchainClient):
    """
    Has the same prerequisites as BlockchainClient
    """

    def __init__(self, config_filepath: str = 'blockchain_config.json') -> None:
        """
        Connect with running IPFS node.
        """
        super().__init__(config_filepath)

    # helper function implementation

    def _learn(self, model=dict, participants=dict, optimizer=dict):
        """
        Helper function for decentralized_learn.
        Provided a model and a list of participants who are expected to
        train this model, uploads the model packaged with the optimizer to
        IPFS and then stores a pointer on the blockchain.

        params
        @model: dict returned by make_model()
        @participants: dict returned by make_participants()
        @optimizer: dict returned by make_optimizer()
        """
        job_to_post = {}
        job_to_post["job_uuid"] = model.get("job_uuid", str(uuid.uuid4()))
        job_to_post["serialized_model"] = model["serialized_model"]
        # NOTE: Currently we only support Keras, so this is hardcoded
        job_to_post["framework_type"] = model.get("framework_type", "keras")
        job_to_post["hyperparams"] = model["hyperparams"]
        # We post the participants as well so that each participant will know 
        # which keys to accept messages from in the future
        new_session_event = {
            TxEnum.KEY.name: None,
            TxEnum.CONTENT.name: {
                "optimizer_params": optimizer,
                "serialized_job": job_to_post,
                "participants": participants
            }
        }
        # Add dict to IPFS for later retrieval over blockchain
        key_vals = [self._upload(self.client, participant) for
                            participant in participants]
        on_chain_value = self.client.add_json(new_session_event)
        # Currently, by definition a 'new session' tx has key==value.
        # If this changes in future, then this should also be changed.
        txs = [Transaction(key_val, on_chain_value, round_num=0) for key_val in key_vals]
        timeout = time.time() + self.timeout
        tx_receipts = []
        # Post to blockchain
        for tx in txs:
            while time.time() < timeout:
                try:
                    tx_receipts.append(self._make_setter_call(self.host, self.port, tx.get_tx()))
                    break
                except (UnboundLocalError, requests.exceptions.ConnectionError) as e:
                    logging.info("HTTP SET error, got: {0}".format(e))
                    continue
        return on_chain_value, tx_receipts

    def _make_model(self, model: object, batch_size: int=32, 
                    epochs: int=10, split: float=1, avg_type: str="data_size"):
        """
        Helper function for decentralized_learning
        Returns model_dict

        params
        @model: Keras model
        @batch_size: minibatch size for data
        @epochs: number of epochs to train for
        @split: split for data in raw_filepath
        @avg_type: averaging type for decentralized learning
        """
        assert avg_type in ['data_size', 'val_acc'], \
            "Averaging type '{0}' is not supported.".format(avg_type)
        model_dict = {}
        model_json = model.to_json()
        model_dict["serialized_model"] = model_json
        hyperparams = {}
        hyperparams["batch_size"] = batch_size
        hyperparams["epochs"] = epochs
        hyperparams["split"] = split
        hyperparams["averaging_type"] = avg_type
        model_dict["hyperparams"] = hyperparams
        return model_dict
    
    def _validate_participants(self, participants: dict):
        """
        Helper function for decentralized_learn.
        Returns a list of participants = [
            {'dataset_uuid': uuid,
            'label_column_name': label}
        ]
        For the MVP, all participants will see this long dict. They will lookup their own
        name, to get the uuid of their dataset and the label_column_name for their dataset.
        NOTE: Currently this function only tests the label_column_name
        but in future, it could do more.
        """
        # TODO: This should be updated once we have a better schema for
        # what the participants dict will look like.
        assert all(["label_column_name" in dct for dct in participants]), \
            "Supervised learning needs a column to be specified as the label column"
    
    def _make_optimizer(self, opt_type="FEDERATED_AVERAGING", 
                        num_rounds=1, num_averages_per_round=1):
        """
        Helper function for decentralized_learn.
        Returns a dict optimizer_params
        NOTE: Currently the only parameter that "really" needs to be set is
        num_rounds
        """
        assert opt_type in ["FEDERATED_AVERAGING", "CLOUD_CONNECTED"], \
            "Optimizer '{0}' is not supported.".format(opt_type)
        optimizer_params = {
            "optimizer_type": opt_type,
            "num_averages_per_round": num_averages_per_round, 
            "max_rounds": num_rounds
        }
        return optimizer_params

    def decentralized_learn(self, model: object, participants, batch_size: int=32, 
            epochs: int=10, split: float=1, avg_type: str="data_size",
            opt_type="FEDERATED_AVERAGING", num_rounds=1):
        """
        Public method exposed to Explora to enable end users to submit decentralized
        training session instantiations to the blockchain.

        Calls three helper functions and has some preset parameters.
        """
        model_dict = self._make_model(
            model=model,
            batch_size=batch_size,
            epochs=epochs,
            split=split,
            avg_type=avg_type
        )
        optimizer_params = self._make_optimizer(
            opt_type=opt_type,
            num_rounds=num_rounds,
            # this means that each node has to wait for all other nodes
            # before moving on. (well, technically RN n-1 since key management but)
            num_averages_per_round=len(participants),
        )
        self._validate_participants(participants)
        keys, receipt = self._learn(
            model=model_dict,
            optimizer=optimizer_params,
            participants=participants
        )
        return keys
