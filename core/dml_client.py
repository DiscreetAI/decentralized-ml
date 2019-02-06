import json
import logging
import requests
import time

import ipfsapi
from keras import optimizers

from core.blockchain_client import BlockchainClient, TxEnum, Transaction


def get_optimizer(model):
    def get_json_type(obj):
        """Serialize any object to a JSON-serializable structure.
        # Arguments
            obj: the object to serialize
        # Returns
            JSON-serializable structure representing `obj`.
        # Raises
            TypeError: if `obj` cannot be serialized.
        """
        # if obj is a serializable Keras class instance
        # e.g. optimizer, layer
        if hasattr(obj, 'get_config'):
            return {'class_name': obj.__class__.__name__,
                    'config': obj.get_config()}

        # if obj is any numpy type
        if type(obj).__module__ == np.__name__:
            if isinstance(obj, np.ndarray):
                return {'type': type(obj),
                        'value': obj.tolist()}
            else:
                return obj.item()

        # misc functions (e.g. loss function)
        if callable(obj):
            return obj.__name__

        # if obj is a python 'type'
        if type(obj).__name__ == type.__name__:
            return obj.__name__

        raise TypeError('Not JSON Serializable:', obj)

    if model.optimizer:
        metadata = {}
        if isinstance(model.optimizer, optimizers.TFOptimizer):
            warnings.warn(
                'TensorFlow optimizers do not '
                'make it possible to access '
                'optimizer attributes or optimizer state '
                'after instantiation. '
                'As a result, we cannot save the optimizer '
                'as part of the model save file.'
                'You will have to compile your model again '
                'after loading it. '
                'Prefer using a Keras optimizer instead '
                '(see keras.io/optimizers).')
        else:
            metadata['training_config'] = json.dumps({
                'optimizer_config': {
                    'class_name': model.optimizer.__class__.__name__,
                    'config': model.optimizer.get_config()
                },
                'loss': model.loss,
                'metrics': model.metrics,
                'sample_weight_mode': model.sample_weight_mode,
                'loss_weights': model.loss_weights,
            }, default=get_json_type)

    return metadata

logging.basicConfig(level=logging.DEBUG,
    format='[DMLClient] %(message)s')

class DMLClient(BlockchainClient):
    """
    Has the same prerequisites as BlockchainClient
    """

    def __init__(self, config: object) -> None:
        """
        Connect with running IPFS node.
        """
        super().__init__(config)

    # helper function implementation

    def _learn(self, model=dict, participants=dict, optimizer=dict, job_uuid=str):
        """
        Helper function for decentralized_learn.
        Provided a model and a list of participants who are expected to
        train this model, uploads the model packaged with the optimizer to
        IPFS and then stores a pointer on the blockchain.

        params
        @model: dict returned by make_model()
        @participants: dict returned by make_participants()
        @optimizer: dict returned by make_optimizer()
        @job_uuid: unique identifier for job
        """
        job_to_post = {}
        job_to_post["job_uuid"] = job_uuid
        job_to_post["serialized_model"] = model["serialized_model"]
        # NOTE: Currently we only support Keras, so this is hardcoded
        job_to_post["framework_type"] = model.get("framework_type", "keras")
        job_to_post["hyperparams"] = model["hyperparams"]
        # We post the participants as well so that each participant will know 
        # which keys to accept messages from in the future
        new_session_event = {
                "optimizer_params": optimizer,
                "serialized_job": job_to_post,
                "participants": participants
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
        model_architecture = model.to_json()
        model_optimizer = get_optimizer(model)
        model_json = {
            "architecture": model_architecture,
            "optimizer": model_optimizer
        }
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

    def decentralized_learn(self, job_uuid, model: object, participants, batch_size: int=32, 
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
            participants=participants,
            job_uuid=job_uuid
        )
        return keys
