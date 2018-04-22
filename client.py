import logging
import pickle
import shutil

import numpy as np
import tensorflow as tf

from models.perceptron import Perceptron
from models.cnn import CNN
from models.lstm import LSTM

logging.basicConfig(level=logging.DEBUG,
                    format='[Client] %(asctime)s %(levelname)s %(message)s')

class Client(object):
    def __init__(self, iden, X_train, y_train):
        self.iden = iden
        self.X_train = X_train
        self.y_train = y_train

    def setup_model(self, model_type):
        self.model_type = model_type
        if model_type == "perceptron":
            self.model = Perceptron()
        elif model_type == "cnn-mnist":
            self.model = CNN()
        elif model_type == "lstm":
            self.model = LSTM()
        else:
            raise ValueError("Model {0} not supported.".format(model_type))

    # def setup_training(self, batch_size, epochs, learning_rate):
    #     self.batch_size = self.X_train.shape[0] if batch_size == -1 else batch_size
    #     self.epochs = epochs
    #     self.params = {'learning_rate': learning_rate}

    def train(self, weights, config):
        logging.info('Training just started.')
        assert weights != None, 'weights must not be None.'
        batch_size = self.X_train.shape[0] if config["batch_size"] == -1 \
            else config["batch_size"]
        epochs = config["epochs"]
        learning_rate = config["learning_rate"]
        params = {'new_weights': weights, 'learning_rate': learning_rate}

        classifier = tf.estimator.Estimator(
            model_fn=self.model.get_model,
            model_dir=self.get_checkpoints_folder(),
            params = params
        )
        # tensors_to_log = {"probabilities": "softmax_tensor"}
        # logging_hook = tf.train.LoggingTensorHook(
        #     tensors=tensors_to_log, every_n_iter=50)
        train_input_fn = tf.estimator.inputs.numpy_input_fn(
            x={"x": self.X_train},
            y=self.y_train,
            batch_size=batch_size,
            num_epochs=epochs,
            shuffle=True
        )
        classifier.train(
            input_fn=train_input_fn,
            # steps=1
            # hooks=[logging_hook]
        )
        logging.info('Training complete.')
        new_weights = self.model.get_weights(self.get_latest_checkpoint())
        shutil.rmtree("./checkpoints-{0}/".format(self.iden))
        return new_weights, self.X_train[0].size

    def get_checkpoints_folder(self):
        return "./checkpoints-{0}/{1}/".format(self.iden, self.model_type)

    def get_latest_checkpoint(self):
        return tf.train.latest_checkpoint(self.get_checkpoints_folder())
