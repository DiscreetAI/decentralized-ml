import numpy as np
import tensorflow as tf

from models.generic_model import GenericModel

class Perceptron(GenericModel):
    def __init__():
        self.n_input = 784 # MNIST data input (img shape: 28*28)
        self.n_classes = 10 # MNIST total classes (0-9 digits)
        self.weights = {
            'h1': tf.Variable(tf.random_normal([n_input, n_hidden_1])),
            'h2': tf.Variable(tf.random_normal([n_hidden_1, n_hidden_2])),
            'out': tf.Variable(tf.random_normal([n_hidden_2, n_classes]))
        }
        self.biases = {
            'b1': tf.Variable(tf.random_normal([n_hidden_1])),
            'b2': tf.Variable(tf.random_normal([n_hidden_2])),
            'out': tf.Variable(tf.random_normal([n_classes]))
        }
        self.x = tf.placeholder("float", [None, self.n_input])
        self.y = tf.placeholder("float", [None, self.n_classes])

    def build(self):
        # Hidden layer with RELU activation
        layer_1 = tf.add(tf.matmul(self.x, self.weights['h1']), self.biases['b1'])
        layer_1 = tf.nn.relu(layer_1)
        # Hidden layer with RELU activation
        layer_2 = tf.add(tf.matmul(layer_1, self.weights['h2']), self.biases['b2'])
        layer_2 = tf.nn.relu(layer_2)
        # Output layer with linear activation
        out_layer = tf.matmul(layer_2, self.weights['out']) + self.biases['out']
        self.output = out_layer

    def initialize_weights(self):
        self.init = tf.global_variables_initializer()
        return self.init

    def setup_optimizer(self, learning_rate):
        self.cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=self.output, labels=self.y))
        self.optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

    def load_weights(self):
        pass

    def get_weights(self):
        return (self.weights, self.biases)

    def sum_weights(self, weights1, weights2):
        pass

    def scale_weights(self, weights, factor):
        pass
