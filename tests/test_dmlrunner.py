import tests.context

import pytest
import numpy as np

from core.runner                import DMLRunner
from core.configuration         import ConfigurationManager
from core.utils.keras           import serialize_weights
from core.utils.enums           import JobTypes
from tests.testing_utils        import make_initialize_job, make_model_json
from tests.testing_utils        import make_train_job, make_validate_job, make_hyperparams


@pytest.fixture
def config_manager():
    config_manager = ConfigurationManager()
    config_manager.bootstrap(
        config_filepath='tests/artifacts/runner_scheduler/configuration.ini'
    )
    return config_manager

def test_dmlrunner_initialize_job_returns_list_of_nparray(config_manager):
    model_json = make_model_json()
    runner = DMLRunner(config_manager)
    initialize_job = make_initialize_job(model_json)
    result = runner.run_job(initialize_job)
    results = result.results
    initial_weights = results['weights']
    assert result.job.job_type is JobTypes.JOB_INIT.name
    assert type(initial_weights) == list
    assert type(initial_weights[0]) == np.ndarray


def test_dmlrunner_train_job_returns_weights_omega_and_stats(config_manager):
    model_json = make_model_json()
    hyperparams = make_hyperparams()
    runner = DMLRunner(config_manager)
    initialize_job = make_initialize_job(model_json)
    initial_weights = runner.run_job(initialize_job).results['weights']
    train_job = make_train_job(model_json, initial_weights, hyperparams)
    result = runner.run_job(train_job)
    results = result.results
    new_weights = results['weights']
    omega = results['omega']
    train_stats = results['train_stats']
    assert result.job.job_type is JobTypes.JOB_TRAIN.name
    assert type(new_weights) == list
    assert type(new_weights[0]) == np.ndarray
    assert type(omega) == int or type(omega) == float
    assert type(train_stats) == dict


def test_dmlrunner_validate_job_returns_stats(config_manager):
    model_json = make_model_json()
    hyperparams = make_hyperparams()
    runner = DMLRunner(config_manager)
    initialize_job = make_initialize_job(make_model_json())
    initial_weights = runner.run_job(initialize_job).results['weights']
    train_job = make_train_job(model_json, initial_weights, hyperparams)
    result = runner.run_job(train_job)
    results = result.results
    new_weights = results['weights']
    omega = results['omega']
    train_stats = results['train_stats']
    hyperparams['split'] = 1 - hyperparams['split']
    validate_job = make_validate_job(model_json, new_weights, hyperparams)
    result = runner.run_job(validate_job)
    results = result.results
    val_stats = results['val_stats']
    assert result.job.job_type is JobTypes.JOB_VAL.name
    assert type(val_stats) == dict
