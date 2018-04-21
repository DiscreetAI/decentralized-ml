import numpy as np
import tensorflow as tf

from models.generic_model import GenericModel

class Perceptron(GenericModel):
    def __init__(self):
        self.n_input = 784
        self.n_hidden1 = 200
        self.n_hidden2 = 200
        self.n_classes = 10

    def preprocess_input(self, x):
        return x

    def build_model(self, input_layer):
        new_weights = self.new_weights if hasattr(self, 'new_weights') else None
        get_tensor_name = lambda l, t: new_weights['/'.join([l, "dense", t]) + ":0"]

        layer_name = "layer1"
        with tf.variable_scope(layer_name):
            kernel_init, bias_init = None, None
            if new_weights:
                kernel_init = tf.constant_initializer(get_tensor_name(layer_name, "kernel"))
                bias_init = tf.constant_initializer(get_tensor_name(layer_name, "bias"))
            self.layer1 = tf.layers.dense(input_layer, self.n_hidden1, tf.nn.relu,
                kernel_initializer=kernel_init, bias_initializer=bias_init)

        layer_name = "layer2"
        with tf.variable_scope(layer_name):
            kernel_init, bias_init = None, None
            if new_weights:
                kernel_init = tf.constant_initializer(get_tensor_name(layer_name, "kernel"))
                bias_init = tf.constant_initializer(get_tensor_name(layer_name, "bias"))
            self.layer2 = tf.layers.dense(self.layer1, self.n_hidden2, tf.nn.relu,
                kernel_initializer=kernel_init, bias_initializer=bias_init)

        layer_name = "logits_layer"
        with tf.variable_scope(layer_name):
            kernel_init, bias_init = None, None
            if new_weights:
                kernel_init = tf.constant_initializer(get_tensor_name(layer_name, "kernel"))
                bias_init = tf.constant_initializer(get_tensor_name(layer_name, "bias"))
            self.logits = tf.layers.dense(self.layer2, self.n_classes,
                kernel_initializer=kernel_init, bias_initializer=bias_init)

    def build_loss(self):
        self.loss = tf.losses.sparse_softmax_cross_entropy(
            labels=self.labels,
            logits=self.logits,
            loss_collection=tf.GraphKeys.LOSSES
        )

    def build_optimizer(self):
        optimizer = tf.train.GradientDescentOptimizer(learning_rate=self.learning_rate)
        self.optimizer = optimizer.minimize(
            loss=self.loss,
            global_step=tf.train.get_global_step(),
            name='train_op'
        )

    def build_predictions_obj(self):
        logits = self.logits
        classes = tf.argmax(input=self.logits, axis=1, name="classes_tensor")
        probabilities = tf.nn.softmax(self.logits, name="softmax_tensor")

        tf.add_to_collection('predictions', logits)
        tf.add_to_collection('predictions', classes)
        tf.add_to_collection('predictions', probabilities)

        self.predictions = {
            "logits": logits,
            "classes": classes,
            "probabilities": probabilities
        }

    def build_eval_metric(self):
        self.eval_metric_ops = {
          "accuracy": tf.metrics.accuracy(labels=self.labels, predictions=self.predictions["classes"])
        }

    def get_estimator(self, mode):
        estimator = None
        self.build_predictions_obj()
        if mode == tf.estimator.ModeKeys.PREDICT:
            self.build_eval_metric()
            estimator = tf.estimator.EstimatorSpec(mode=mode, predictions=self.predictions)
        elif mode == tf.estimator.ModeKeys.TRAIN:
            self.build_loss()
            self.build_optimizer()
            estimator = tf.estimator.EstimatorSpec(mode=mode, loss=self.loss, train_op=self.optimizer)
        elif mode == tf.estimator.ModeKeys.EVAL:
            self.build_loss()
            self.build_eval_metric()
            estimator = tf.estimator.EstimatorSpec(mode=mode, loss=self.loss, eval_metric_ops=self.eval_metric_ops)
        return estimator


    def get_model(self, features, labels, mode, params):
        """
        When using the Estimator API, features will come as a TF Tensor already.
        """
        # Set up hyperparameters.
        if params:
            self.learning_rate = params.get("learning_rate", None)
            self.new_weights = params.get("new_weights", None)

        # Do pre-processing if necessary.
        self.input_layer = self.preprocess_input(features["x"])
        self.labels = labels

        # Define the model.
        self.build_model(self.input_layer)

        # Build and return the estimator.
        return self.get_estimator(mode)

    def load_weights(self, new_weights, latest_checkpoint, checkpoint_dir):
        tf.reset_default_graph()
        with tf.Session().as_default() as sess:
            new_saver = tf.train.import_meta_graph(latest_checkpoint + '.meta')
            # To load non-trainable variables and prevent errors...
            # we restore them if they are found, or initialize them otherwise.
            try:
                new_saver.restore(sess, latest_checkpoint)
            except:
                sess.run(tf.global_variables_initializer())

            collection = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES)
            for tensor in collection:
                assign_op = tensor.assign(new_weights[tensor.name])
                sess.run(assign_op)

            save_path = new_saver.save(sess, checkpoint_dir + "model.ckpt")
        tf.reset_default_graph()

    def get_weights(self, latest_checkpoint):
        tf.reset_default_graph()
        graph = tf.Graph()
        with tf.Session(graph=graph) as sess:
            new_saver = tf.train.import_meta_graph(latest_checkpoint + '.meta')
            new_saver.restore(sess, latest_checkpoint)
            collection = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES)
            weights = {tensor.name:sess.run(tensor) for tensor in collection}
        return weights

    def sum_weights(self, weights1, weights2):
        new_weights = {}
        for key1, key2 in zip(sorted(weights1.keys()), sorted(weights2.keys())):
            assert key1 == key2, 'Error with keys'
            new_weights[key1] = weights1[key1] + weights2[key2]
        return new_weights

    def scale_weights(self, weights, factor):
        new_weights = {}
        for key, value in weights.items():
            new_weights[key] = value * factor
        return new_weights

    def inverse_scale_weights(self, weights, factor):
        new_weights = {}
        for key, value in weights.items():
            new_weights[key] = value / factor
        return new_weights
