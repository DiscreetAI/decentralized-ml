import numpy as np

from core.utils.keras import deserialize_weights

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
    for i, serialized_weights in enumerate(list_of_serialized_weights):
        weights_list = []
        for j in range(len(serialized_weights)):
            deserialized_weight = np.array(np.fromstring(serialized_weights[i]))
            weights_list.append(deserialized_weight * omegas[i])
        averaged_weights.append(sum(weights_list) / sum(omegas))
    return averaged_weights
