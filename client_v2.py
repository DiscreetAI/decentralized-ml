import os
import logging
import pickle
import shutil
import random
import uuid

import numpy as np
import tensorflow as tf
import keras

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
        self.iden = uuid.uuid4()[:8]
        self.dataset_path = dataset_path
        self.config = config
        # self.full_dataset_iterator = create_dataset_iterator(dataset_path)
        # self.train_dataset_iterator, self.val_dataset_iterator = \
        #     create_split_dataset_iterators(dataset_path, split=0.8)

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
        assert avg_type in ['data_size', 'val_acc'],
            "Averaging type '{0}' is not supported.".format(avg_type)
        if avg_type == 'data_size':
            dataset_iterator = create_dataset_iterator(self.dataset_path, \
                batch_size=batch_size, labeler=mnist_labeler) # Hard-coded labeler.
        elif avg_type == 'val_acc':
            dataset_iterators = create_split_dataset_iterators(self.dataset_path, \
                batch_size=batch_size, labeler=mnist_labeler) # Hard-coded labeler.
            dataset_iterator, test_dataset_iterator = dataset_iterators

        # Train the model the right way based on the model type.
        assert model_type in ['keras'], \
            "Model type '{0}' is not supported.".format(model_type)
        if model_type == 'keras':
            new_weights, train_stats = train_keras_model(serialized_model,
                initial_weights, dataset_iterator, stopping_conditions,
                hyperparams)

        # Get the right omega based on the averaging type.
        if avg_type == 'data_size':
            dataset_iterator = create_dataset_iterator(self.dataset_path, \
                batch_size=batch_size, labeler=mnist_labeler) # Hard-coded labeler.
            omega = sum(1 for _ in dataset_iterator)
        elif avg_type == 'val_acc':
            val_stats = self.validate(serialized_model, model_type,
                new_weights, custom_iterator=test_dataset_iterator)
            omega = val_stats['val_metric']
            train_stats.update(val_stats)

        # Return the results.
        return new_weights, omega, train_stats

    def validate(self, serialized_model, model_type, weights, custom_iterator=None):
        """
        Validates on all the local data the specified machine learning model at
        the state specified.

        Returns the metrics returned by the model.
        """
        # Choose the dataset to validate on.
        if custom_iterator is None:
            dataset_iterator = create_dataset_iterator(self.dataset_path, \
                labeler=mnist_labeler) # Hard-coded labeler.
        else:
            dataset_iterator = custom_iterator

        # Validate the model the right way based on the model type.
        assert model_type in ['keras'], \
            "Model type '{0}' is not supported.".format(model_type)
        if model_type == 'keras':
            val_stats = validate_keras_model(serialized_model, weights,
                dataset_iterator)

        # Return the validation stats.
        return val_stats

    def initialize_model(self):
        """
        Initializes the model weights as specified in the model and returns them.
        """
        assert model_type in ['keras'], \
            "Model type '{0}' is not supported.".format(model_type)
        if model_type == 'keras':
            initial_weights = self.model.get_initial_weights()
        return initial_weights


def train_keras_model(serialized_model, weights, dataset_iterator, hyperparams):
    logging.info('Keras training just started.')
    assert weights != None, "Initial weights must not be 'None'."
    self.model.set_weights(weights)
    hist = self.model.fit_generator(dataset_iterator, epochs=hyperparams['epochs'])
    new_weights = self.model.get_weights()
    logging.info('Keras training complete.')
    return new_weights, {'training_history' : hist.history}


def validate_keras_model(serialized_model, weights, dataset_iterator):
    logging.info('Keras validation just started.')
    assert initial_weights != None, "Initial weights must not be 'None'."
    self.model.set_weights(initial_weights)
    history = self.model.evaluate_generator(dataset_iterator)
    logging.info('Keras validation complete.')
    return {'val_metric': history}


def create_dataset_iterator(dataset_path, batch_size, labeler):
    """
    INCOMPLETE

    Returns an iterator of batches of size B containing all features of the data.

    Assumes `dataset_path` is a path to a folder with multiple CSV files.
    """
    for filename in os.listdir(dataset_path):
        if not filename.endswith(".csv"): continue
        full_path = os.path.join(dataset_path, filename)
        with open(full_path, 'r') as f:
            batch = []
            for line in f:
                if len(batch) == batch_size:
                    yield


def create_split_dataset_iterators(dataset_path, batch_size, labeler, split=0.8):
    """
    Assumes `dataset_path` is a path to a folder with multiple CSV files.
    """
    pass



# class TensorflowClient(object):
#     def __init__(self, iden, X, y):
#         self.iden = iden
#         self.X = X
#         self.y = y
#
#         # TODO: Should be randomized.
#         cut_off = int(X.shape[0] * 0.8)
#         self.X_train = X[:cut_off]
#         self.y_train = y[:cut_off]
#         self.X_test = X[cut_off:]
#         self.y_test = y[cut_off:]
#
#     def setup_model(self, model_type):
#         self.model_type = model_type
#         if model_type == "perceptron":
#             self.model = Perceptron()
#         elif model_type == "cnn-mnist":
#             self.model = CNN()
#         elif model_type == "cnn-cifar10":
#             self.model = CNN()
#         else:
#             raise ValueError("Model {0} not supported.".format(model_type))
#
#     def train(self, weights, config):
#         logging.info('Training just started.')
#         assert weights != None, 'weights must not be None.'
#
#         assert config["averaging_type"] in ["data_size", "val_acc"]
#         if config["averaging_type"] == "data_size":
#             X, y = self.X, self.y
#         elif config["averaging_type"] == "val_acc":
#             X, y = self.X_train, self.y_train
#
#         batch_size = X.shape[0] \
#             if config["batch_size"] == -1 else config["batch_size"]
#         epochs = config["epochs"]
#         learning_rate = config["learning_rate"]
#         params = {'new_weights': weights, 'learning_rate': learning_rate}
#
#         classifier = tf.estimator.Estimator(
#             model_fn=self.model.get_model,
#             model_dir=self.get_checkpoints_folder(),
#             params = params
#         )
#         train_input_fn = tf.estimator.inputs.numpy_input_fn(
#             x={"x": X},
#             y=y,
#             batch_size=batch_size,
#             num_epochs=epochs,
#             shuffle=True
#         )
#         classifier.train(input_fn=train_input_fn)
#         logging.info('Training complete.')
#         new_weights = self.model.get_weights(self.get_latest_checkpoint())
#
#         if config["averaging_type"] == "data_size":
#             omega = X.shape[0]
#         elif config["averaging_type"] == "val_acc":
#             eval_classifier = tf.estimator.Estimator(
#                 model_fn=self.model.get_model,
#                 model_dir=self.get_checkpoints_folder(),
#                 params = {'new_weights': new_weights}
#             )
#             eval_input_fn = tf.estimator.inputs.numpy_input_fn(
#                 x={"x": self.X_test},
#                 y=self.y_test,
#                 num_epochs=1,
#                 shuffle=False
#             )
#             eval_results = eval_classifier.evaluate(input_fn=eval_input_fn)
#             omega = eval_results["accuracy"]
#
#         shutil.rmtree("./checkpoints-{0}/".format(self.iden))
#         return new_weights, omega
#
#     def validate(self, t, weights, config):
#         # check if this is needed
#         model_type = config["model_type"]
#         self.setup_model(model_type)
#         classifier = tf.estimator.Estimator(
#             model_fn=self.model.get_model,
#             model_dir=self.get_checkpoints_folder(),
#             params = {'new_weights': weights, 'learning_rate': 0.0}
#         )
#         train_input_fn = tf.estimator.inputs.numpy_input_fn(
#             x={"x": self.X},
#             y=self.y,
#             batch_size=1,
#             num_epochs=None,
#             shuffle=False
#         )
#         classifier.train(
#             input_fn=train_input_fn,
#             steps=1
#         )
#
#         metagraph_file = self.get_checkpoints_folder() + '.meta'
#         self.model.load_weights(weights, self.get_latest_checkpoint(),
#             self.get_checkpoints_folder())
#         logging.info('Main model updated.')
#
#         self.setup_model(model_type)
#         classifier = tf.estimator.Estimator(
#             model_fn=self.model.get_model,
#             model_dir=self.get_checkpoints_folder(),
#             params = {'new_weights': weights}
#         )
#         eval_input_fn = tf.estimator.inputs.numpy_input_fn(
#             x={"x": self.X},
#             y=self.y,
#             num_epochs=1,
#             shuffle=False
#         )
#         eval_results = classifier.evaluate(input_fn=eval_input_fn)
#         logging.info("[Round {0}] Validation results: {1}".format(t, eval_results))
#         return eval_results
#
#     def get_initial_weights(self, model_type):
#         tf.reset_default_graph()
#         if model_type == "perceptron":
#             m = Perceptron()
#             inputs = tf.placeholder(tf.float32, shape=(None, 28*28))
#             _ = m.get_model(features={"x": inputs}, labels=None, mode='predict', params=None)
#         elif model_type == 'cnn-mnist':
#             m = CNN()
#             inputs = tf.placeholder(tf.float32, shape=(None, 28, 28, 1))
#             _ = m.get_model(features={"x": inputs}, labels=None, mode='predict', params=None)
#         elif model_type == 'cnn-cifar10':
#             m = CNN()
#             inputs = tf.placeholder(tf.float32, shape=(None, 32, 32, 3))
#             _ = m.get_model(features={"x": inputs}, labels=None, mode='predict', params=None)
#         else:
#             raise ValueError("Model {model_type} not supported.".format(model_type))
#         with tf.Session().as_default() as sess:
#             sess.run(tf.global_variables_initializer())
#             collection = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES)
#             weights = {tensor.name:sess.run(tensor) for tensor in collection}
#         tf.reset_default_graph()
#         return weights
#
#     def get_checkpoints_folder(self):
#         return "./checkpoints-{0}/{1}/".format(self.iden, self.model_type)
#
#     def get_latest_checkpoint(self):
#         return tf.train.latest_checkpoint(self.get_checkpoints_folder())
#
# class KerasClient(object):
#     def __init__(self, iden, X, y):
#         self.iden = iden
#         self.X = X
#         self.y = y
#
#     def setup_model(self, model_type):
#         self.model_type = model_type
#         if model_type == "lstm":
#             self.model = LSTMModel()
#         else:
#             raise ValueError("Model {0} not supported.".format(model_type))
#
#     def train(self, weights, config):
#         logging.info('Training just started.')
#         assert weights != None, 'weights must not be None.'
#         self.model.set_weights(weights)
#         self.model.train(X)
#         logging.info('Training complete.')
#         new_weights = self.model.get_weights()
#         return new_weights, len(X)
#
#     def validate(self, t, weights, config):
#         # TODO: Need to implement Keras validation.
#         pass
#
#     def get_initial_weights(self):
#         return self.model.get_initial_weights()
