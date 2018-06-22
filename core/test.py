"""Gotta move this somewhere else @panda. Lease expires on EOW."""

import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import json
import keras
from custom.keras import model_from_serialized, get_optimizer

from blockchain.ipfs_utils import *

if __name__ == '__main__':
    from models.keras_perceptron import KerasPerceptron
    m = KerasPerceptron(is_training=True)
    model_architecture = m.model.to_json()
    model_optimizer = get_optimizer(m.model)
    model_json = {
        "architecture": model_architecture,
        "optimizer": model_optimizer
    }
    addr = push_model(model_json)
    print(ipfs2base32(addr))
    # model_json = get_model(base322ipfs(ipfs2base32(addr)))
    # print(model_json)
