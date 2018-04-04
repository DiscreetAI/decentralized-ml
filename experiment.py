from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import logging
import random
import os

import numpy as np
import tensorflow as tf

from server import Server
from client import Client

logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s %(levelname)s %(message)s')
os.environ["TF_CPP_MIN_LOG_LEVEL"]="3"
#logging.getLogger('tensorflow').disabled = True

# Set random seeds for reproducibility.
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
tf.set_random_seed(RANDOM_SEED)

class Experiment:
    def __init__(self, config):
        logging.info('Starting experiment.')
        self.config = config
        # self.host = config['host']
        # self.port = config['port']
        self.num_clients = config['num_clients']
        self.model_type = config['model_type']
        self.dataset_type = config['dataset_type']
        self.fraction = config['fraction']
        self.max_rounds = config['max_rounds']

        # Set up datasets
        logging.info('Setting up datasets.')
        X_train_list, y_train_list, X_test, y_test = \
            self.get_datasets(self.num_clients, self.model_type, self.dataset_type)

        # Make the clients and server and connect them
        logging.info('Setting up server and clients.')
        self.clients = []
        i = 1
        for X, y in zip(X_train_list, y_train_list):
            self.clients.append(Client(i, X, y))
            i += 1
        #self.server = Server(self.clients, X_test, y_test)
        self.server = Server(self.clients, X_train_list[0], y_train_list[0])

        # Set up models
        logging.info('Setting up the deep models.')
        self.batch_size = config['batch_size']
        self.epochs = config['epochs']
        self.learning_rate = config['learning_rate']
        for client in self.clients:
            client.setup_model(self.model_type)
            client.setup_training(self.batch_size, self.epochs, self.learning_rate)
        logging.info('Done setting up experiment.')

    def get_datasets(self, num_clients, model_type, dataset_type):
        # Load training and eval data
        if model_type == 'perceptron':
            mnist = tf.contrib.learn.datasets.load_dataset("mnist")
            X_train = np.concatenate((mnist.train.images, mnist.validation.images))
            y_train = np.concatenate((
                        np.asarray(mnist.train.labels, dtype=np.int32),
                        np.asarray(mnist.validation.labels, dtype=np.int32),
                      ))
            X_test = mnist.test.images
            y_test = np.asarray(mnist.test.labels, dtype=np.int32)

            X_train = X_train.reshape(-1, 784)
            X_test = X_test.reshape(-1, 784)
        else:
            raise ValueError('Model type {0} not supported.'.format(model_type))

        # Partition data
        if dataset_type == 'iid':
            # Shuffle data (train and test)
            indices = np.random.permutation(X_train.shape[0])
            X_train, y_train = X_train[indices], y_train[indices]
            indices = np.random.permutation(X_test.shape[0])
            X_test, y_test = X_test[indices], y_test[indices]

            # Partition data
            X_train_list = np.split(X_train, num_clients)
            y_train_list = np.split(y_train, num_clients)
        else:
            raise ValueError('Dataset type {0} not supported.'.format(dataset_type))

        return X_train_list, y_train_list, X_test, y_test

    def run(self):
        self.server.federated_learning(self.fraction, self.max_rounds, self.model_type)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--clients', type=int, help="number of clients \
        to instantiate (default 1)")
    parser.add_argument('-m', '--model', type=str, help="type of deep model \
        (specifies the dataset) (default perceptron)")
    parser.add_argument('-d', '--datasettype', type=str, help="type of dataset \
        partition (default IID)")
    parser.add_argument('-c', '--fraction', type=float, help="fraction of \
        clients to train on (default 1.0)")
    parser.add_argument('-r', '--maxrounds', type=int, help="maximum number \
        of communication rounds (default 100000)")
    parser.add_argument('-b', '--batchsize', type=int, help="local batchsize \
        (default 50)")
    parser.add_argument('-e', '--epochs', type=int, help="number of local \
        epochs (-1 implies the whole dataset) (default 50)")
    parser.add_argument('-l', '--learningrate', type=float, help="learning rate \
        (default 1e-4)")
    # parser.add_argument('-hh', '--host', type=str, help="hostname (default \
    #     127.0.0.1)")
    # parser.add_argument('-p', '--port', type=str, help="port (default 12345)")
    args = parser.parse_args()

    k = args.clients if args.clients else 1
    m = args.model if args.model else 'perceptron'
    d = args.datasettype if args.datasettype else 'iid'
    c = args.fraction if args.fraction else 1.0
    r = args.maxrounds if args.maxrounds else 100000
    b = args.batchsize if args.batchsize else 50
    e = args.epochs if args.epochs else 10
    l = args.learningrate if args.learningrate else 1e-4
    # h = args.host if args.host else '127.0.0.1'
    # p = args.port if args.port else 12345

    config = {
        "num_clients": k,
        "model_type": m,
        "dataset_type": d,
        "fraction": c,
        "max_rounds": r,
        "batch_size": b,
        "epochs": e,
        "learning_rate": l,
        # "host": h,
        # "port": p
    }

    experiment = Experiment(config)

    experiment.run()
