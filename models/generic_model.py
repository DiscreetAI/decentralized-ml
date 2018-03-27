import logging

import numpy as np
import tensorflow as tf


class GenericModel:
    """
    Generic Model Class

    Each subclass of this class needs to define the data structure of its weights
    (which should be respected accross methods) and implement the functions below.

    """

    def build(self):
        raise NotImplementedError("Subclasses should implement this!")

    def initialize_weights(self):
        raise NotImplementedError("Subclasses should implement this!")

    def setup_optimizer(self, learning_rate):
        raise NotImplementedError("Subclasses should implement this!")

    def load_weights(self):
        raise NotImplementedError("Subclasses should implement this!")

    def get_weights(self):
        raise NotImplementedError("Subclasses should implement this!")

    def sum_weights(self, weights1, weights2):
        raise NotImplementedError("Subclasses should implement this!")

    def scale_weights(self, weights, factor):
        raise NotImplementedError("Subclasses should implement this!")

    def inverse_scale_weights(self, weights, factor):
        raise NotImplementedError("Subclasses should implement this!")
