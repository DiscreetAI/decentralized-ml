#!/usr/bin/env python

import json
import requests

import ipfsapi

from tests.testing_utils import make_serialized_job
serialized_job = make_serialized_job('tests/artifacts/integration/mnist')
new_session_event = {
         "KEY": None,
         "CONTENT": {
             "optimizer_params": {"num_averages_per_round": 2, "max_rounds": 5},
             "serialized_job": serialized_job
         }
}

client = ipfsapi.connect('127.0.0.1', 5001)
content_hash = client.add_json(new_session_event)

headers = {
    "Content-Type": "application/json",
}

data = {
    "KEY": str(content_hash),
    "CONTENT": str(content_hash),
}

r = requests.post(
    'http://127.0.0.1:3001/txs',
    headers=headers,
    data=json.dumps(data),
)

if r.status_code == requests.codes.ok:
    print("OK")
else:
    print("Error")
