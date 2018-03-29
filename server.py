from multiprocessing.pool import Pool
import random
from math import ceil
import logging
import pathlib

import numpy as np
import tensorflow as tf

from models.perceptron import Perceptron

logging.basicConfig(level=logging.DEBUG,
                    format='[Server] %(asctime)s %(levelname)s %(message)s')

class Server:
    def __init__(self, clients, X_test, y_test):
        # Since this architecture doesn't use sockets, we will
        # ignore the host and the port.
        self.clients = clients
        self.X_test = X_test
        self.y_test = y_test

    def setup_model(self, model_type):
        self.model_type = model_type
        if model_type == "perceptron":
            self.model = Perceptron()
        else:
            raise ValueError("Model {model_type} not supported." \
                .format(model_type))

    # def initialize_model(self):
    #     tf.reset_default_graph()
    #     with tf.Session().as_default() as sess:
    #         self.model.build_all()
    #         sess.run(tf.global_variables_initializer())
    #
    #         collection = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES)
    #         for tensor in collection:
    #             assign_op = tensor.assign(weights[tensor.name])
    #             sess.run(assign_op)
    #
    #         save_path = new_saver.save(sess, "./mnist/model.ckpt", global_step=round_num)

    def federated_learning(self, fraction, max_rounds):
        #self.initialize_model()
        
        for t in range(max_rounds):
            logging.info('Round number {0}.'.format(t+1))
            m = max( ceil(fraction * len(self.clients)), 1 )
            random_clients = random.sample(self.clients, m)

            threads = []
            pool = Pool(processes=m)
            if t == 0:
                current_weights = None
            else:
                current_weights = self.model.get_weights(self.get_latest_checkpoint())
            print('$$$', current_weights)
            for k, client in enumerate(random_clients):
                res = pool.apply_async(client.train, (current_weights,))
                threads.append(res)

            weights, metagraph, n = threads[0].get()
            for res in threads[1:]:
                update, _, num_data = res.get()
                update = self.model.scale_weights(update, num_data)
                weights = self.model.sum_weights(weights, update)
                n += num_data
            if max_rounds > 1:
                weights = self.model.inverse_scale_weights(update, n)

            pathlib.Path(self.get_checkpoints_folder()).mkdir(parents=True, exist_ok=True)
            metagraph_file = self.get_checkpoints_folder() + 'model.meta'
            with open(metagraph_file, 'wb+') as f:
                f.write(metagraph)
            f.close()

            self.model.load_weights(weights, metagraph_file, self.get_checkpoints_folder())
            logging.info('Main model updated.')
            self.validate_model(t)

    def validate_model(self, t):
        classifier = tf.estimator.Estimator(
            model_fn=self.model.get_model,
            model_dir=self.get_checkpoints_folder()
        )
        eval_input_fn = tf.estimator.inputs.numpy_input_fn(
            x={"x": self.X_test},
            y=self.y_test,
            num_epochs=1,
            shuffle=False
        )
        eval_results = classifier.evaluate(input_fn=eval_input_fn)
        logging.info("[Round {0}] Validation results: {1}".format(t, eval_results))

    def get_checkpoints_folder(self):
        return "./checkpoints/" + self.model_type + '/'

    def get_latest_checkpoint(self):
        return tf.train.latest_checkpoint(self.get_checkpoints_folder())
