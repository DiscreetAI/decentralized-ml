import os
import uuid
import json

import keras
import tensorflowjs as tfjs

import state

TEMP_FOLDER = 'temp'

def convert_and_save_model(h5_model_path):
    session_id = state.state["session_id"]
    round = state.state["current_round"]
    converted_model_path = os.path.join(TEMP_FOLDER, session_id, str(round))
    _keras_2_tfjs(h5_model_path, converted_model_path)

    metadata = {
        "session_id": session_id,
        "current_round": round,
    }
    with open(converted_model_path + '/metadata.json', 'w') as fp:
        json.dump(metadata, fp, sort_keys=True, indent=4)

    return converted_model_path

def _keras_2_tfjs(h5_model_path, path_to_save):
    """
    Do Keras stuff here
    """
    model = keras.models.load_model(h5_model_path)
    tfjs.converters.save_keras_model(model, path_to_save)


def _test():
    state.init()
    out = convert_and_save_model('../notebooks/saved_mlp_model_with_w.h5')
    print(out)


# def decode_weights(h5_model_path):
#     """
#     Do Keras stuff here
#     """
#     model = keras.models.load_model(h5_model_path)
#     weights = model.get_weights()
#     return weights


# def _test2():
#     out = decode_weights('../notebooks/saved_mlp_model_with_w.h5')
#     print(out)
