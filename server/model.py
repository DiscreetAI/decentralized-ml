import os
import uuid

import keras
import tensorflowjs as tfjs

TEMP_FOLDER = 'temp'

def decode_weights(h5_model):
    """
    Do Keras stuff here
    """
    pass

def keras_2_tfjs(h5_model_path):
    """
    Do Keras stuff here
    """
    model = keras.models.load_model(h5_model_path)
    converted_model_path = os.path.join(TEMP_FOLDER, str(uuid.uuid4()))
    tfjs.converters.save_keras_model(model, converted_model_path)
    return converted_model_path


def _test():
    out = keras_2_tfjs('../notebooks/saved_mlp_model_with_w.h5')
    print(out)
