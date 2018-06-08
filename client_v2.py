import logging
import random
import uuid

import numpy as np
import tensorflow as tf
import keras

from custom.keras import model_from_serialized, get_optimizer
from examples.labelers import mnist_labeler # Should be removed for labeler interoperability.
from data.iterators import count_datapoints
from data.iterators import create_train_dataset_iterator
from data.iterators import create_test_dataset_iterator

logging.basicConfig(level=logging.DEBUG,
                    format='[Client] %(asctime)s %(levelname)s %(message)s')

class DMLClient(object):
    """
    DML Client

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
        Sets up the unique identifier of the DML Client and the local dataset path.
        """
        self.iden = str(uuid.uuid4())[:8]
        self.dataset_path = dataset_path
        self.config = config
        self.data_count = count_datapoints(dataset_path)

    def train(self, serialized_model, model_type, initial_weights, hyperparams):
        """
        Trains the specified machine learning model on all the local data,
        starting from the initial model state specified, until a stopping
        condition is met, and using the hyper-parameters specified.

        Returns the updated model weights, the weighting factor omega, and stats
        about the training job.

        NOTE: Should probably have a function to preprocess/create labels from
        the raw data. This function would be called `labeler`.
        """
        # Get the right dataset iterator based on the averaging type.
        avg_type = hyperparams['averaging_type']
        batch_size = hyperparams['batch_size']
        assert avg_type in ['data_size', 'val_acc'], \
            "Averaging type '{0}' is not supported.".format(avg_type)
        if avg_type == 'data_size':
            dataset_iterator = create_train_dataset_iterator(self.dataset_path, \
                count=self.data_count, split=self.config['split'], \
                batch_size=batch_size, labeler=mnist_labeler)
        elif avg_type == 'val_acc':
            dataset_iterators = create_train_dataset_iterator(self.dataset_path, \
                count=self.data_count, batch_size=batch_size, labeler=mnist_labeler)
            test_dataset_iterator = create_test_dataset_iterator(self.dataset_path, \
                count=self.data_count, split=self.config['split'], \
                batch_size=batch_size, labeler=mnist_labeler)

        # Train the model the right way based on the model type.
        assert model_type in ['keras'], \
            "Model type '{0}' is not supported.".format(model_type)
        if model_type == 'keras':
            new_weights, train_stats = train_keras_model(serialized_model,
                initial_weights, dataset_iterator, \
                self.data_count*self.config['split'], hyperparams)

        # Get the right omega based on the averaging type.
        if avg_type == 'data_size':
            omega = self.data_count * self.config['split']
        elif avg_type == 'val_acc':
            val_stats = self.validate(serialized_model, model_type, new_weights,
                custom_iterator=test_dataset_iterator)
            omega = val_stats['val_metric']
            train_stats.update(val_stats)

        # Return the results.
        return new_weights, omega, train_stats

    def validate(self, serialized_model, model_type, weights, hyperparams,
        custom_iterator=None):
        """
        Validates on all the local data the specified machine learning model at
        the state specified.

        Returns the metrics returned by the model.
        """
        # Choose the dataset to validate on.
        batch_size = hyperparams['batch_size']
        if custom_iterator is None:
            dataset_iterator = create_test_dataset_iterator(self.dataset_path, \
                count=self.data_count, split=(1-self.config['split']), \
                batch_size=batch_size, labeler=mnist_labeler)
        else:
            dataset_iterator = custom_iterator

        # Validate the model the right way based on the model type.
        assert model_type in ['keras'], \
            "Model type '{0}' is not supported.".format(model_type)
        if model_type == 'keras':
            val_stats = validate_keras_model(serialized_model, weights,
                dataset_iterator, self.data_count*(1-self.config['split']))

        # Return the validation stats.
        return val_stats

    def initialize_model(self, serialized_model, model_type):
        """
        Initializes and returns the model weights as specified in the model.
        """
        assert model_type in ['keras'], \
            "Model type '{0}' is not supported.".format(model_type)
        if model_type == 'keras':
            model = model_from_serialized(serialized_model)
            initial_weights = model.get_weights()
        return initial_weights


def train_keras_model(serialized_model, weights, dataset_iterator, data_count, hyperparams):
    logging.info('Keras training just started.')
    assert weights != None, "Initial weights must not be 'None'."
    model = model_from_serialized(serialized_model)
    model.set_weights(weights)
    hist = model.fit_generator(dataset_iterator, epochs=hyperparams['epochs'], \
        steps_per_epoch=data_count//hyperparams['batch_size'])
    new_weights = model.get_weights()
    logging.info('Keras training complete.')
    return new_weights, {'training_history' : hist.history}


def validate_keras_model(serialized_model, weights, dataset_iterator, data_count):
    logging.info('Keras validation just started.')
    assert weights != None, "weights must not be 'None'."
    model = model_from_serialized(serialized_model)
    model.set_weights(weights)
    history = model.evaluate_generator(dataset_iterator, steps=data_count)
    metrics = dict(zip(model.metrics_names, history))
    logging.info('Keras validation complete.')
    return {'val_metric': metrics}


if __name__ == '__main__':
    config = {
        'split': 0.8,
    }

    client = DMLClient('datasets/mnist', config)

    from models.keras_perceptron import KerasPerceptron
    m = KerasPerceptron(is_training=True)
    model_architecture = m.model.to_json()
    model_optimizer = get_optimizer(m.model)
    model_json = {
        "architecture": model_architecture,
        "optimizer": model_optimizer
    }
    print(model_json)

    initial_weights = client.initialize_model(model_json, 'keras')

    hyperparams = {
        'averaging_type': 'data_size',
        'batch_size': 50,
        'epochs': 2,
    }

    new_weights, omega, train_stats = \
        client.train(model_json, 'keras', initial_weights, hyperparams)
    print(train_stats)

    val_stats = client.validate(model_json, 'keras', new_weights, hyperparams)
    print(val_stats)
