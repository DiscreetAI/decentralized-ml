import tests.context

import pytest
import numpy as np

from core.runner                import DMLRunner
from custom.keras               import get_optimizer
from models.keras_perceptron    import KerasPerceptron
from core.utils.dmljob          import DMLJob
from core.configuration         import ConfigurationManager


@pytest.fixture
def config_manager():
    config_manager = ConfigurationManager()
    config_manager.bootstrap(
        config_filepath='tests/artifacts/configuration.ini'
    )
    return config_manager


def make_dataset_path():
    return 'datasets/mnist'


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


def make_train_job(model_json, initial_weights, hyperparams):
    train_job = DMLJob(
        "train",
        model_json,
        "keras",
        initial_weights,
        hyperparams,
        0
    )
    return train_job


def make_validate_job(model_json, new_weights, hyperparams):
    validate_job = DMLJob(
        "validate",
        model_json,
        'keras',
        new_weights,
        hyperparams,
        0
    )
    return validate_job


def test_dmlrunner_initialize_job_returns_list_of_nparray(config_manager):
    model_json = make_model_json()
    runner = DMLRunner(config_manager)
    initialize_job = make_initialize_job(model_json)
    initial_weights = runner.run_job(initialize_job)['return_obj']
    assert type(initial_weights) == list
    assert type(initial_weights[0]) == np.ndarray


def test_dmlrunner_train_job_returns_weights_omega_and_stats(config_manager):
    model_json = make_model_json()
    hyperparams = make_hyperparams()
    runner = DMLRunner(config_manager)
    initialize_job = make_initialize_job(model_json)
    initial_weights = runner.run_job(initialize_job)['return_obj']
    train_job = make_train_job(model_json, initial_weights, hyperparams)
    new_weights, omega, train_stats = runner.run_job(train_job)['return_obj']
    assert type(new_weights) == list
    assert type(new_weights[0]) == np.ndarray
    assert type(omega) == int or type(omega) == float
    assert type(train_stats) == dict


def test_dmlrunner_validate_job_returns_stats(config_manager):
    model_json = make_model_json()
    hyperparams = make_hyperparams()
    runner = DMLRunner(config_manager)
    initialize_job = make_initialize_job(make_model_json())
    initial_weights = runner.run_job(initialize_job)['return_obj']
    train_job = make_train_job(model_json, initial_weights, hyperparams)
    new_weights, omega, train_stats = runner.run_job(train_job)['return_obj']
    hyperparams['split'] = 1 - hyperparams['split']
    validate_job = make_validate_job(model_json, new_weights, hyperparams)
    val_stats = runner.run_job(validate_job)['return_obj']
    assert type(val_stats) == dict
