import ipfsapi
import json
from filelock import FileLock
import base58

from keras.models import load_model, model_from_json


api = ipfsapi.connect('127.0.0.1', 5001)
CONFIG = None

# print('starting to load model from IPFS')
# catted = api.cat('QmVm4yB2jxPwXXVXM6n86TuwA4jCQ7EfNPjguFrhoCbPiJ')
# print('loaded in model from IPFS as bytes')
# model = model.load_weights(catted)
def ipfs2keras(model, model_address):
    deserialize_keras_model(model, api.cat(model_address))
    return 'Hoorah'
def deserialize_keras_model(model, model_bin):
    lock = FileLock('models/temp_model.h5.lock')
    with lock:
        with open('models/temp_model.h5', 'wb') as g:
            g.write(model_bin)
            g.close()
        model.load_weights('models/temp_model.h5')
# ipfs2keras(catted)
# print('I loaded a model from IPFS!')
def keras2ipfs(model):
    return api.add_bytes(serialize_keras_model(model))
def serialize_keras_model(model):
    lock = FileLock('models/temp_model.h5.lock')
    with lock:
        model.load_weights('models/temp_model.h5')
        with open('models/temp_model.h5', 'rb') as f:
            model_bin = f.read()
            f.close()
        return model_bin
def json2bytes32(json):
    content_hash = api.add_json(json)
    bytes_array = base58.b58decode(content_hash) 
    return bytes_array[2:]

# def send_model():
#     dict_of_stuff = keras2ipfs()
#     return dict_of_stuff
# if __name__ == '__main__':
    # print(ipfs2base32('QmZf6NVYgxTMA6996744sbakRN9Ks8xE6HWAEb3x6JN5i9'))
    # print(base322ipfs(ipfs2base32('QmZf6NVYgxTMA6996744sbakRN9Ks8xE6HWAEb3x6JN5i9')))