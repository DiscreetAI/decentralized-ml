# Decentralized Machine Learning [![Build Status](https://travis-ci.org/georgymh/decentralized-ml.svg?branch=master)](https://travis-ci.org/georgymh/decentralized-ml)

## Instructions

To try out the project, just clone or download it and then run the following instructions on CLI:

```
export DB_PASS="datashark"
```

```
python setup.py develop
```

```
dml
```

If this is your first time running the project, it will ask you to fill out certain configurations. You can safely choose the default options by just pressing *Enter* multiple times, or you can manually enter your own preferences.

After this, the service will be running on your machine and you can stop it at any time by pressing *Ctrl-C*.

## Run Decentralized Training

### Prerequisites

Make sure ipfs is running in a new window with ```ipfs daemon```

Make sure the chain is running on another window with ```node app_trivial.js```

### Creating a new DML Session
The following is an example for uploading a new DML Session to the IPFS, and subsequently uploading a pointer to that IPFS entry to the blockchain. All available nodes will hear this and begin participating in your session if possible.

```
python3
>>> import ipfsapi
>>> client = ipfsapi.connect('127.0.0.1','5001')
>>> from tests.testing_utils import make_serialized_job
>>> serialized_job = make_serialized_job('tests/artifacts/integration/mnist')
>>> new_session_event = {
...         "KEY": None,
...         "CONTENT": {
...             "optimizer_params": {"listen_bound": 2, "total_bound": 2},
...             "serialized_job": serialized_job
...         }
...     }
>>> session = client.add_json(new_session_event)
'QmVg5aAsSuv2HuUSYNEAKQCQHHPb25gZxQ36gaMSUdBTSX'
>>> exit()
curl --header "Content-Type: application/json"   --request POST   --data '{"CONTENT": "QmVg5aAsSuv2HuUSYNEAKQCQHHPb25gZxQ36gaMSUdBTSX",
"KEY": "QmVg5aAsSuv2HuUSYNEAKQCQHHPb25gZxQ36gaMSUdBTSX" }'   http://localhost:3000/txs
```
