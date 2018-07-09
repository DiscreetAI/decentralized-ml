import pytest

import tests.context

import numpy as np
from custom.keras               import get_optimizer
from core.runner                import DMLRunner
from models.keras_perceptron    import KerasPerceptron
from core.utils.dmljob          import DMLJob, serialize_job, deserialize_job
from examples.labelers          import mnist_labeler


def make_dataset_path():
    return 'datasets/mnist'


def make_config():
    return {}


def make_model_json():
    m = KerasPerceptron(is_training=True)
    model_architecture = m.model.to_json()
    model_optimizer = get_optimizer(m.model)
    model_json = {
        "architecture": model_architecture,
        "optimizer": model_optimizer
    }
    return model_json


def make_hyperparams():
    hyperparams = {
        'averaging_type': 'data_size',
        'batch_size': 4,
        'epochs': 1,
        'split': 0.004,
    }
    return hyperparams


def make_initialize_job(model_json):
    initialize_job = DMLJob(
        "initialize",
        model_json,
        "keras"
    )
    return initialize_job


def make_train_job(model_json, initial_weights, config, hyperparams):
    train_job = DMLJob(
        "train",
        model_json,
        "keras",
        config,
        initial_weights,
        hyperparams,
        mnist_labeler
    )
    return train_job


def make_validate_job(model_json, new_weights, config, hyperparams):
    validate_job = DMLJob(
        "validate",
        model_json,
        'keras',
        config,
        new_weights,
        hyperparams,
        mnist_labeler
    )
    return validate_job


def test_dmlrunner_initialize_job_returns_list_of_nparray():
    model_json = make_model_json()
    runner = DMLRunner(make_dataset_path(), make_config())
    initialize_job = make_initialize_job(model_json)
    initial_weights = runner.run_job(initialize_job)
    assert type(initial_weights) == list
    assert type(initial_weights[0]) == np.ndarray


def test_dmlrunner_train_job_returns_weights_omega_and_stats():
    model_json = make_model_json()
    hyperparams = make_hyperparams()
    config = make_config()
    runner = DMLRunner(make_dataset_path(), make_config())
    initialize_job = make_initialize_job(model_json)
    initial_weights = runner.run_job(initialize_job)
    train_job = make_train_job(model_json, initial_weights, config, hyperparams)
    new_weights, omega, train_stats = runner.run_job(train_job)
    assert type(new_weights) == list
    assert type(new_weights[0]) == np.ndarray
    assert type(omega) == int or type(omega) == float
    assert type(train_stats) == dict


def test_dmlrunner_validate_job_returns_stats():
    model_json = make_model_json()
    hyperparams = make_hyperparams()
    config = make_config()
    runner = DMLRunner(make_dataset_path(), make_config())
    initialize_job = make_initialize_job(make_model_json())
    initial_weights = runner.run_job(initialize_job)
    train_job = make_train_job(model_json, initial_weights, config, hyperparams)
    new_weights, omega, train_stats = runner.run_job(train_job)
    hyperparams['split'] = 1 - hyperparams['split']
    validate_job = make_validate_job(model_json, new_weights, config, hyperparams)
    val_stats = runner.run_job(validate_job)
    assert type(val_stats) == dict
