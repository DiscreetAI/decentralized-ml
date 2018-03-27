import numpy as np
import tensorflow as tf


class Perceptron:
    def __init__(self, hparams):
        self.n_input = 784
        self.n_classes = 10
        self.n_hidden1 = 200
        self.n_hidden2 = 200
        self.learning_rate = hparams['learning_rate']

    def preprocess_input(self, x):
        return x

    def build_model(self, input_layer):
        with tf.variable_scope("layer1"):
            self.layer1 = tf.layers.dense(input_layer, self.n_hidden1, tf.nn.relu)
        with tf.variable_scope("layer2"):
            self.layer2 = tf.layers.dense(self.layer1, self.n_hidden2, tf.nn.relu)
        with tf.variable_scope("logits_layer"):
            self.logits = tf.layers.dense(self.layer2, self.n_classes)

    def build_loss(self):
        self.loss = tf.losses.sparse_softmax_cross_entropy(labels=self.labels, logits=self.logits)

    def build_optimizer(self):
        optimizer = tf.train.AdamOptimizer(learning_rate=self.learning_rate)
        self.optimizer = optimizer.minimize(
            loss=self.loss,
            global_step=tf.train.get_global_step()
        )

    def build_predictions_obj(self):
        self.predictions = {
            "logits": self.logits,
            "classes": tf.argmax(input=self.logits, axis=1),
            "probabilities": tf.nn.softmax(self.logits, name="softmax_tensor")
        }

    def build_eval_metric(self):
        self.eval_metric_ops = {
          "accuracy": tf.metrics.accuracy(labels=self.labels, predictions=self.predictions["classes"])
        }

    def get_estimator(self, mode):
        estimator = None
        if mode == tf.estimator.ModeKeys.PREDICT:
            self.build_predictions_obj()
            self.build_eval_metric()
            estimator = tf.estimator.EstimatorSpec(mode=mode, predictions=self.predictions)
        elif mode == tf.estimator.ModeKeys.TRAIN:
            self.build_loss()
            self.build_optimizer()
            estimator = tf.estimator.EstimatorSpec(mode=mode, loss=self.loss, train_op=self.optimizer)
        elif mode == tf.estimator.ModeKeys.EVAL:
            self.build_eval_metric()
            self.build_loss()
            estimator = tf.estimator.EstimatorSpec(mode=mode, loss=self.loss, eval_metric_ops=self.eval_metric_ops)
        return estimator

    def get_model(self, features, labels, mode):
        """
        When using the Estimator API, features will come as a TF Tensor already.
        """
        # Do pre-processing if necessary.
        self.input_layer = self.preprocess_input(features["x"])
        self.labels = labels

        # Define the model.
        self.build_model(self.input_layer)

        # Build and return the estimator.
        return self.get_estimator(mode)
