import logging
import random
import uuid
import time

from custom.keras import model_from_serialized, get_optimizer
from data.iterators import count_datapoints
from data.iterators import create_train_dataset_iterator
from data.iterators import create_test_dataset_iterator
from core.utils.keras import train_keras_model, validate_keras_model
from core.utils.keras import serialize_weights
from core.configuration import ConfigurationManager


logging.basicConfig(level=logging.DEBUG,
                    format='[Runner] %(asctime)s %(levelname)s %(message)s')


class DMLRunner(object):
    """
    DML Runner

    This class manages the training and validation of a DML job. It trains or
    validate a specified machine learning model on a local dataset. An instance
    of this class has a one-to-one relationship with a DML job, and gets freed up
    for another DML job after executing the job. Once free, it can schedule a new
    DML job from any DML session and repeat the cycle.

    Note that this class does not schedule how jobs received should be executed
    nor listens to incoming jobs. This class only executes the jobs.

    """

    def __init__(self, config_manager):
        """
        Sets up the unique identifier of the DML Runner and the local dataset path.
        """
        config = config_manager.get_config()
        self.iden = str(uuid.uuid4())[:8]
        self.dataset_path = config.get("GENERAL", "dataset_path")
        self.config = dict(config.items("RUNNER"))
        self.data_count = count_datapoints(self.dataset_path)

    def run_job(self, job):
        """
        Identifies a DMLJob type and executes it.

        If the runner is already executing a job, it silently does nothing.
        """
        assert job.job_type in ['train', 'validate', 'initialize'], \
            'DMLJob type ({0}) is not valid'.format(job.job_type)
        logging.info("Running job (type: {0})...".format(job.job_type))
        if job.job_type == 'train':
            new_weights, omega, train_stats = self._train(
                job.serialized_model,
                job.model_type,
                job.weights,
                job.hyperparams,
                job.labeler
            )
            # TODO: Send the (new_weights_in_bytes, omega) to the aggregator
            # through P2P.
            print(train_stats)
            return_obj = new_weights, omega, train_stats
        elif job.job_type == 'validate':
            val_stats = self._validate(
                 job.serialized_model,
                 job.model_type,
                 job.weights,
                 job.hyperparams,
                 job.labeler
            )

            # TODO: Send the results to the developer through P2P (maybe).
            # How are we getting this metadata (val_stats) back to the user?
            # This has been assigned to Neelesh ^
            print(val_stats)
            return_obj = val_stats
        elif job.job_type == 'initialize':
            # NOTE: This shouldn't be used in BETA/PROD right now, only DEV!!!
            initial_weights = self._initialize_model(
                job.serialized_model,
                job.model_type
            )
            weights_in_bytes = serialize_weights(initial_weights)
            # TODO: Send (weights_in_bytes) to all nodes/aggregator/developer
            # through P2P.
            #print(initial_weights)
            return_obj = initial_weights
        self.current_job = None
        logging.info("Finished running job!")
        return return_obj # Returning is only for debugging purposes.

    def _train(self, serialized_model, model_type, initial_weights, hyperparams,
        labeler):
        """
        Trains the specified machine learning model on all the local data,
        starting from the initial model state specified, until a stopping
        condition is met, and using the hyper-parameters specified.

        Returns the updated model weights, the weighting factor omega, and stats
        about the training job.

        NOTE: Uses the same hyperparameters and labeler for training and
        validating during 'avg_type' of type 'val_acc'.

        NOTE2: Assumes 'initial_weights' are the actual weights and not a path.
        """
        # Get the right dataset iterator based on the averaging type.
        avg_type = hyperparams['averaging_type']
        batch_size = hyperparams['batch_size']
        assert avg_type in ['data_size', 'val_acc'], \
            "Averaging type '{0}' is not supported.".format(avg_type)
        logging.info("Training model...")
        if avg_type == 'data_size':
            dataset_iterator = create_train_dataset_iterator(self.dataset_path, \
                count=self.data_count, split=hyperparams['split'], \
                batch_size=batch_size, labeler=labeler)
        elif avg_type == 'val_acc':
            dataset_iterator = create_train_dataset_iterator(self.dataset_path, \
                count=self.data_count, batch_size=batch_size, labeler=labeler)
            test_dataset_iterator = create_test_dataset_iterator(self.dataset_path, \
                count=self.data_count, split=hyperparams['split'], \
                batch_size=batch_size, labeler=labeler)

        # Train the model the right way based on the model type.
        assert model_type in ['keras'], \
            "Model type '{0}' is not supported.".format(model_type)
        if model_type == 'keras':
            new_weights_path, train_stats = train_keras_model(serialized_model,
                initial_weights, dataset_iterator, \
                self.data_count*hyperparams['split'], hyperparams, self.config)

        # Get the right omega based on the averaging type.
        if avg_type == 'data_size':
            omega = self.data_count * hyperparams['split']
        elif avg_type == 'val_acc':
            val_stats = self._validate(serialized_model, model_type, new_weights,
                hyperparams, labeler, custom_iterator=test_dataset_iterator)
            omega = val_stats['val_metric']['acc']
            train_stats.update(val_stats)

        # Return the results.
        return new_weights_path, omega, train_stats

    def _validate(self, serialized_model, model_type, weights, hyperparams,
        labeler, custom_iterator=None):
        """
        Validates on all the local data the specified machine learning model at
        the state specified.

        Returns the metrics returned by the model.

        NOTE: Assumes 'weights' are the actual weights and not a path.
        """
        logging.info("Validating model...")
        # Choose the dataset to validate on.
        batch_size = hyperparams['batch_size']
        if custom_iterator is None:
            dataset_iterator = create_test_dataset_iterator(self.dataset_path, \
                count=self.data_count, split=(1-hyperparams['split']), \
                batch_size=batch_size, labeler=labeler)
        else:
            dataset_iterator = custom_iterator

        # Validate the model the right way based on the model type.
        assert model_type in ['keras'], \
            "Model type '{0}' is not supported.".format(model_type)
        if model_type == 'keras':
            val_stats = validate_keras_model(serialized_model, weights,
                dataset_iterator, self.data_count*(1-hyperparams['split']))

        # Return the validation stats.
        return val_stats

    def _initialize_model(self, serialized_model, model_type):
        """
        Initializes and returns the model weights as specified in the model.
        """
        assert model_type in ['keras'], \
            "Model type '{0}' is not supported.".format(model_type)
        logging.info("Initializing model...")
        if model_type == 'keras':
            model = model_from_serialized(serialized_model)
            model.summary()
            initial_weights = model.get_weights()
        return initial_weights
