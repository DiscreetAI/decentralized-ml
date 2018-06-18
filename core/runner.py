# Add the parent directory to the PATH to allow imports.
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import logging
import random
import uuid

from custom.keras import model_from_serialized, get_optimizer
from data.iterators import count_datapoints
from data.iterators import create_train_dataset_iterator
from data.iterators import create_test_dataset_iterator
from core.utils.keras import train_keras_model, validate_keras_model
from blockchain.ipfs_utils import *


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

    def __init__(self, dataset_path, config):
        """
        Sets up the unique identifier of the DML Runner and the local dataset path.
        """
        self.iden = str(uuid.uuid4())[:8]
        self.dataset_path = dataset_path
        self.config = config
        self.data_count = count_datapoints(dataset_path)
        self.current_job = None

    def run_job(self, job):
        """
        Identifies a DMLJob type and executes it.

        If the runner is already executing a job, it silently does nothing.
        """
        assert job.job_type in ['train', 'validate', 'initialize'], \
            'DMLJob type ({0}) is not valid'.format(job.job_type)
        if self.is_active(): return
        logging.info("Running job (type: {0})...".format(job.job_type))
        self.current_job = job
        if job.job_type == 'train':
            new_weights_path, omega, train_stats = self._train(
                job.serialized_model,
                job.model_type,
                job.weights,
                job.hyperparams,
                job.labeler
            )
            print(new_weights_path)
            exit(1)
            # TODO: Send the results to the aggregator through P2P.
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
            # TODO: Send the results to the aggregator through P2P.
            print(val_stats)
            return_obj = val_stats
        elif job.job_type == 'initialize':
            initial_weights = self._initialize_model(
                job.serialized_model,
                job.model_type
            )
            # TODO: Send the results to the aggregator through P2P.
            return_obj = initial_weights
        self.current_job = None
        logging.info("Finished running job!")
        return return_obj # Returning is only for debugging purposes.

    def is_active(self):
        """
        Returns whether the runner is running a job.
        """
        return self.current_job != None

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


if __name__ == '__main__':
    config = {}

    runner = DMLRunner('datasets/mnist', config)

    from models.keras_perceptron import KerasPerceptron
    m = KerasPerceptron(is_training=True)
    model_architecture = m.model.to_json()
    model_optimizer = get_optimizer(m.model)
    model_json = {
        "architecture": model_architecture,
        "optimizer": model_optimizer
    }
    # @panda: why do we need to test this here?
    addr = push_model(model_json)
    model_json = get_model(base322ipfs(ipfs2base32(addr)))
    ###########################################
    # print(model_json)

    from core.utils.dmljob import DMLJob
    initialize_job = DMLJob(
        "initialize",
        model_json,
        "keras"
    )
    initial_weights = runner.run_job(initialize_job)

    hyperparams = {
        'averaging_type': 'data_size',
        'batch_size': 50,
        'epochs': 2,
        'split': 0.8,
    }

    from examples.labelers import mnist_labeler
    train_job = DMLJob(
        "train",
        model_json,
        "keras",
        config,
        initial_weights,
        hyperparams,
        mnist_labeler
    )
    new_weights, omega, train_stats = runner.run_job(train_job)

    validate_job = DMLJob(
        "validate",
        model_json,
        'keras',
        config,
        new_weights,
        hyperparams,
        mnist_labeler
    )
    val_stats = runner.run_job(validate_job)
