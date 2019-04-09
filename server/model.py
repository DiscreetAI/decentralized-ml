import os
import uuid
import json
import base64

import keras
import tensorflowjs as tfjs

import state

TEMP_FOLDER = 'temp'

def convert_and_save_b64model(base64_h5_model):
    session_id = state.state["session_id"]
    model_path = os.path.join(TEMP_FOLDER, session_id)

    # Create directory if necessary
    if not os.path.exists(model_path):
        os.makedirs(model_path)

    # Save model on disk
    h5_model_path = model_path + '/model.h5'
    h5_model_bytes = base64.b64decode(base64_h5_model)
    #h5_model_bytestring = h5_model_bytes.
    with open(h5_model_path, 'wb') as fp:
        fp.write(h5_model_bytes)

    # Convert and save model for serving
    return convert_and_save_model(h5_model_path)


def convert_and_save_model(h5_model_path):
    session_id = state.state["session_id"]
    round = state.state["current_round"]
    converted_model_path = os.path.join(TEMP_FOLDER, session_id, str(round))

    _keras_2_tfjs(h5_model_path, converted_model_path)

    metadata_path = converted_model_path + '/metadata.json'
    metadata = {
        "session_id": session_id,
        "current_round": round,
    }
    with open(metadata_path, 'w') as fp:
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
