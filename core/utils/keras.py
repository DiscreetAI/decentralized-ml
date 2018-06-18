import logging
import uuid
import os

import keras

from custom.keras import model_from_serialized
from core.utils.filesys import ensure_dir


logging.basicConfig(level=logging.DEBUG,
                    format='[Utils/Keras] %(asctime)s %(levelname)s %(message)s')

def train_keras_model(serialized_model, weights, dataset_iterator, data_count,
    hyperparams, config):
    logging.info('Keras training just started.')
    assert weights != None, "Initial weights must not be 'None'."
    model = model_from_serialized(serialized_model)
    model.set_weights(weights)
    hist = model.fit_generator(dataset_iterator, epochs=hyperparams['epochs'], \
        steps_per_epoch=data_count//hyperparams['batch_size'])
    weights_filepath = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        config["weights_directory"],
        uuid.uuid4().hex[:8] + ".h5"
    )
    ensure_dir(weights_filepath)
    model.save_weights(weights_filepath)
    logging.info('Keras training complete.')
    return weights_filepath, {'training_history' : hist.history}


def validate_keras_model(serialized_model, weights, dataset_iterator,
    data_count):
    logging.info('Keras validation just started.')
    assert weights != None, "weights must not be 'None'."
    model = model_from_serialized(serialized_model)
    model.set_weights(weights)
    history = model.evaluate_generator(dataset_iterator, steps=data_count)
    metrics = dict(zip(model.metrics_names, history))
    logging.info('Keras validation complete.')
    return {'val_metric': metrics}
