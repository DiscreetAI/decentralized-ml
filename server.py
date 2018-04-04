#import multiprocessing as mp
#from multiprocessing.pool import Pool
import random
from math import ceil
import logging
import pathlib

import numpy as np
import tensorflow as tf
import ray

from models.perceptron import Perceptron

logging.basicConfig(level=logging.DEBUG,
                    format='[Server] %(asctime)s %(levelname)s %(message)s')

class Server:
    def __init__(self, clients, X_test, y_test):
        self.clients = clients
        self.X_test = X_test
        self.y_test = y_test
        print(X_test.shape[0])

    def setup_model(self, model_type):
        self.model_type = model_type
        if model_type == "perceptron":
            self.model = Perceptron()
        else:
            raise ValueError("Model {0} not supported.".format(model_type))

    def get_initial_weights(self, model_type):
        tf.reset_default_graph()
        if model_type == "perceptron":
            m = Perceptron()
            inputs = tf.placeholder(tf.float32, shape=(None, 28*28))
            _ = m.get_model(features={"x": inputs}, labels=None, mode='predict', params=None)
        else:
            raise ValueError("Model {model_type} not supported.".format(model_type))
        with tf.Session().as_default() as sess:
            sess.run(tf.global_variables_initializer())
            collection = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES)
            weights = {tensor.name:sess.run(tensor) for tensor in collection}
        tf.reset_default_graph()
        return weights

    def federated_learning(self, fraction, max_rounds, model_type):
        self.setup_model(model_type)
        weights = self.get_initial_weights(model_type)
        history = {}

        @ray.remote
        def train_model(client, weights):
            return client.train(weights)

        ray.init()
        for t in range(max_rounds):
            logging.info('Round number {0}.'.format(t+1))
            num_clients = max( ceil(fraction * len(self.clients)), 1 )
            random_clients = random.sample(self.clients, num_clients)

            threads = ray.get([train_model.remote(c, weights) for c in random_clients])

            weights, n = threads[0]
            if num_clients > 1:
                for result in threads[1:]:
                    update, num_data = result
                    update = self.model.scale_weights(update, num_data)
                    weights = self.model.sum_weights(weights, update)
                    n += num_data
                weights = self.model.inverse_scale_weights(weights, n)
            self.validate_model(t, weights)

    def validate_model(self, t, weights):
        self.setup_model(self.model_type)
        #pathlib.Path(self.get_checkpoints_folder()).mkdir(parents=True, exist_ok=True)
        classifier = tf.estimator.Estimator(
            model_fn=self.model.get_model,
            model_dir=self.get_checkpoints_folder(),
            params = {'new_weights': weights, 'learning_rate': 0.0}
        )
        train_input_fn = tf.estimator.inputs.numpy_input_fn(
            x={"x": self.X_test},
            y=self.y_test,
            batch_size=1,
            num_epochs=None,
            shuffle=False
        )
        print('training')
        classifier.train(
            input_fn=train_input_fn,
            steps=1
        )

        metagraph_file = self.get_checkpoints_folder() + '.meta'
        self.model.load_weights(weights, self.get_latest_checkpoint(),
            self.get_checkpoints_folder())
        logging.info('Main model updated.')

        self.setup_model(self.model_type)
        classifier = tf.estimator.Estimator(
            model_fn=self.model.get_model,
            model_dir=self.get_checkpoints_folder(),
            params = {'new_weights': weights}
        )
        eval_input_fn = tf.estimator.inputs.numpy_input_fn(
            x={"x": self.X_test},
            y=self.y_test,
            num_epochs=1,
            shuffle=False
        )
        print('eval')
        eval_results = classifier.evaluate(input_fn=eval_input_fn)
        logging.info("[Round {0}] Validation results: {1}".format(t+1, eval_results))

    def get_checkpoints_folder(self):
        return "./checkpoints/" + self.model_type + '/'

    def get_latest_checkpoint(self):
        return tf.train.latest_checkpoint(self.get_checkpoints_folder())
