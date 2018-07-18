import numpy as np

from core.utils.keras import serialize_weights, deserialize_single_weights


def federated_averaging(list_of_serialized_weights):
    """
    Deserializes, averages, and returns the weights in the
    `list_of_serialized_weights`.

    NOTE: Currently only does vanilla Federated Averaging.
    NOTE: doesn't use omega (hard coded right now).
    """
    assert len(list_of_serialized_weights) == 2, \
        "Only supports 2 clients right now, {} given.".format(
        len(list_of_serialized_weights))
    omegas = [0.5, 0.5] # HARDCODED right now.

    # Deserialize and average weights.
    averaged_weights = []
    num_layers = len(list_of_serialized_weights[0])
    for j in range(num_layers):
        layer_weights_list = []
        for i, serialized_weights in enumerate(list_of_serialized_weights):
            bytestring = serialized_weights[j]
            deserialized_weight = deserialize_single_weights(serialized_weights[j])
            layer_weights_list.append(omegas[i] * deserialized_weight)
        averaged_weights.append(sum(layer_weights_list) / sum(omegas))
    return averaged_weights
