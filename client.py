import logging

import numpy as np
import tensorflow as tf

logging.basicConfig(level=logging.DEBUG,
                    format='[Client] %(asctime)s %(levelname)s %(message)s')

class Client(object):
    def __init__(self, X_train, y_train):
        # Since this architecture doesn't use sockets, we will
        # ignore the host and the port.
        self.X_train = X_train
        self.y_train = y_train

    def setup_model(self, model_type):
        if model_type == "perceptron":
            self.model = Perceptron()
        else:
            raise ValueError("Model {model_type} not supported." \
                .format(model_type))

    def setup_training(self, batch_size, epochs, learning_rate):
        self.batch_size = batch_size
        self.epochs = epochs
        self.model.setup_optimizer(learning_rate)

    def train(self, weights):
        logging.info('Training just started.')
        self.model.load_weights(weights)
        classifier = tf.estimator.Estimator(model_fn=self.model, \
            model_dir="/checkpoints/" + self.model_type)
        tensors_to_log = {"probabilities": "softmax_tensor"}
        logging_hook = tf.train.LoggingTensorHook(
            tensors=tensors_to_log, every_n_iter=50)
        train_input_fn = tf.estimator.inputs.numpy_input_fn(
            x={"x": self.X_train},
            y=self.y_train,
            batch_size=self.batch_size,
            num_epochs=self.epochs,
            shuffle=True
        )
        classifier.train(
            input_fn=train_input_fn,
            hooks=[logging_hook]
        )
        logging.info('Training complete.')
        return self.model.get_weights(), self.X_data[0].size
