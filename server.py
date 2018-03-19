from multiprocessing.pool import ThreadPool
import random
from math import ceil
import logging

import numpy as np
import tensorflow as tf

logging.basicConfig(level=logging.DEBUG,
                    format='[Server] %(asctime)s %(levelname)s %(message)s')

class Server:
    def __init__(self, host, port, clients, X_test, y_test):
        # Since this architecture doesn't use sockets, we will
        # ignore the host and the port.
        self.clients = clients
        self.X_test = X_test
        self.y_test = y_test

    def setup_model(self, model_type):
        if model_type == "perceptron":
            self.model = Perceptron()
        else:
            raise ValueError("Model {model_type} not supported." \
                .format(model_type))

    def federated_learning(self, fraction, max_rounds):
        _ = self.model.initialize_weights()
        for t in range(max_rounds):
            logging.info('Round number {0}.'.format(t+1))
            m = max( ceil(fraction * len(self.clients)), 1)
            random_clients = random.sample(self.clients, m)

            threads = []
            pool = Pool(processes=m)
            current_weights = self.model.get_weights()
            for k, client in enumerate(random_clients):
                res = pool.apply_async(client.train, (current_weights,))
                threads.append(res)

            weights, n = threads[0].get()
            for res in threads[1:]:
                update, num_data = res.get()
                update = self.model.scale_weights(update, num_data)
                weights = self.model.sum_weights(weights, update)
                n += num_data
            weights = self.model.scale_weights(update, 1/n)

            self.model.load_weights(weights)
            logging.info('Main model updated.')
            self.validate_model(t)

    def validate_model(self, t):
        classifier = tf.estimator.Estimator(model_fn=self.model, \
            model_dir="/checkpoints/" + model_type)
        eval_input_fn = tf.estimator.inputs.numpy_input_fn(
            x={"x": self.X_test},
            y=self.y_test,
            num_epochs=1,
            shuffle=False
        )
        eval_results = classifier.evaluate(input_fn=eval_input_fn)
        logging.info("[Round {0}] Validation results: {1}".format(t, eval_results))
