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

```
python utils_submit_dml_session_py.py
```

The above command will submit a small DML session to the blockchain, which your running service will be able to pick up on and train. To submit more complex sessions to the blockchain, please use the Explora frontend client.
