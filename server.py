import time
import random
import uuid
import json
import logging
import pathlib
from math import ceil

import numpy as np
import tensorflow as tf
import ray

from models.perceptron import Perceptron
from models.cnn import CNN
from models.lstm import LSTM

logging.basicConfig(level=logging.DEBUG,
                    format='[Server] %(asctime)s %(levelname)s %(message)s')

class Server:
    def __init__(self, clients, X_test, y_test, config):
        self.clients = clients
        self.X_test = X_test
        self.y_test = y_test
        self.config = config
        self.val_history = {
            "duration" : [],
            "config": config,
            "learning_rate": []
        }
        self.save_path = self.config['save_dir'] + "/" + str(uuid.uuid1())

    def setup_model(self, model_type):
        self.model_type = model_type
        if model_type == "perceptron":
            self.model = Perceptron()
        elif model_type == "cnn":
            self.model = CNN()
        elif model_type == "lstm":
            self.model = LSTM()
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
        num_clients = max( ceil(fraction * len(self.clients)), 1 )
        best_accuracy = 0.0
        goal_accuracy = self.config["goal_accuracy"]

        @ray.remote
        def train_model(client, weights, config):
            return client.train(weights, config)

        ray.init(num_cpus=num_clients)
        for t in range(1, max_rounds + 1):
            if best_accuracy > goal_accuracy:
                logging.info("Reached goal accuracy of {0} at round {1}."\
                    .format(goal_accuracy, t))
                break
            start_time = time.time()
            logging.info('Round number {0}.'.format(t+1))
            random_clients = random.sample(self.clients, num_clients)
            threads = ray.get([train_model.remote(c, weights, self.config) for c in random_clients])

            weights, n = threads[0]
            if num_clients > 1:
                for result in threads[1:]:
                    update, num_data = result
                    update = self.model.scale_weights(update, num_data)
                    weights = self.model.sum_weights(weights, update)
                    n += num_data
                weights = self.model.inverse_scale_weights(weights, n)
            eval_results = self.validate_model(t + 1, weights)
            best_accuracy = max(best_accuracy, eval_results["accuracy"])

            # Update validation history
            for key, value in eval_results.items():
                if key not in self.val_history:
                    self.val_history[key] = []
                self.val_history[key].append(float(value))
            elapsed_time = time.time() - start_time
            self.val_history["learning_rate"].append(self.do_learning_rate_decay())
            self.val_history["duration"].append(elapsed_time)

            # Save validation history
            with open(self.save_path, 'w') as f:
                f.write(json.dumps(self.val_history))

        logging.info("Final validation accuracy: {0}.".format(best_accuracy))
        logging.info("Saved results at {0}.".format(self.save_path))
        logging.info("----- Federated Learning Completed -----")

    def validate_model(self, t, weights):
        # check if this is needed
        self.setup_model(self.model_type)
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
        eval_results = classifier.evaluate(input_fn=eval_input_fn)
        logging.info("[Round {0}] Validation results: {1}".format(t, eval_results))
        return eval_results

    def do_learning_rate_decay(self):
        self.config["learning_rate"] *= self.config["lr_decay"]
        logging.info("Learning rate after decay: {0}.".format(self.config["learning_rate"]))
        return self.config["learning_rate"]

    def get_checkpoints_folder(self):
        return "./checkpoints/" + self.model_type + '/'

    def get_latest_checkpoint(self):
        return tf.train.latest_checkpoint(self.get_checkpoints_folder())
