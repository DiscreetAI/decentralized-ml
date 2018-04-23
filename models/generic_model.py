import logging

import numpy as np
import tensorflow as tf


class GenericModel:
    """
    Generic Model Class

    Each subclass of this class needs to define the data structure of its weights
    (which should be respected accross methods) and implement the functions below.

    """

    def get_model(self):
        raise NotImplementedError("Subclasses should implement this!")

    def load_weights(self):
        raise NotImplementedError("Subclasses should implement this!")

    def get_weights(self):
        raise NotImplementedError("Subclasses should implement this!")

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
