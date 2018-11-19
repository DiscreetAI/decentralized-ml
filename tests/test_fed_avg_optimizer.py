import tests.context

import pytest
import numpy as np
import os
import shutil

from tests.testing_utils import make_initialize_job, make_train_job
from tests.testing_utils import make_serialized_job, make_model_json
from tests.testing_utils import make_hyperparams, make_split_job
from core.utils.enums import JobTypes, RawEventTypes, ActionableEventTypes
from core.fed_avg_optimizer import FederatedAveragingOptimizer
from core.runner import DMLRunner
from core.configuration import ConfigurationManager
from data.iterators import count_datapoints


session_filepaths = set()

@pytest.fixture(scope='session')
def config_manager():
    config_manager = ConfigurationManager()
    config_manager.bootstrap(
        config_filepath='tests/artifacts/fed_avg_optimizer/configuration.ini'
    )
    return config_manager

@pytest.fixture(scope='session')
def initialization_payload(small_filepath):
    return {
        "optimizer_params": {"listen_bound": 2, "listen_iterations": 0},
        "serialized_job": make_serialized_job(small_filepath)
    }

@pytest.fixture(scope='session')
def mnist_filepath():
    return 'tests/artifacts/fed_avg_optimizer/mnist'

@pytest.fixture(scope='session')
def transformed_filepath():
    return 'tests/artifacts/fed_avg_optimizer/mnist'+'/transformed'

@pytest.fixture(scope='session')
def transformed_filepath_2():
    return 'tests/artifacts/fed_avg_optimizer/test'+'/transformed'

@pytest.fixture(scope='session', autouse=True)
def cleanup(transformed_filepath, transformed_filepath_2):
    # Will be executed before the first test
    yield
    # Will be executed after the last test
    if os.path.isdir(transformed_filepath):
        shutil.rmtree(transformed_filepath)
    if os.path.isdir(transformed_filepath_2):
        shutil.rmtree(transformed_filepath_2)

@pytest.fixture(scope='session')
def small_filepath():
    return 'tests/artifacts/fed_avg_optimizer/test'

@pytest.fixture(scope='session')
def init_dmlresult_obj(config_manager, small_filepath):
    runner = DMLRunner(config_manager)
    initialize_job = make_initialize_job(make_model_json(), small_filepath)
    result = runner.run_job(initialize_job)
    return result

@pytest.fixture(scope='session')
def split_dmlresult_obj(config_manager, mnist_filepath):
    model_json = make_model_json()
    runner = DMLRunner(config_manager)
    split_job = make_split_job(
                            model_json, 
                            mnist_filepath,
                        )
    split_job.hyperparams['split'] = 0.75
    job_results = runner.run_job(split_job)
    return job_results

@pytest.fixture(scope='session')
def train_dmlresult_obj(config_manager, split_dmlresult_obj, init_dmlresult_obj):
    runner = DMLRunner(config_manager)
    initial_weights = init_dmlresult_obj.results['weights']
    session_filepath = split_dmlresult_obj.results['session_filepath']
    datapoint_count = split_dmlresult_obj.results['datapoint_count']
    train_job = make_train_job(
                    make_model_json(), 
                    initial_weights, 
                    make_hyperparams(split=1),
                    session_filepath,
                    datapoint_count
                )
    result = runner.run_job(train_job)
    return result

def test_optimizer_fails_on_wrong_event_type(initialization_payload):
    optimizer = FederatedAveragingOptimizer(initialization_payload)
    try:
        dummy_payload = {}
        _, _ = optimizer.ask("WRONG_EVENT_TYPE", dummy_payload)
        raise Exception("Optimizer should have failed!")
    except Exception as e:
        assert str(e) == "Invalid callback passed!"

def test_optimizer_can_kickoff(initialization_payload):
    optimizer = FederatedAveragingOptimizer(initialization_payload)
    event_type, job_arr = optimizer.kickoff()
    assert event_type == ActionableEventTypes.SCHEDULE_JOBS.name
    for job in job_arr:
        assert job.job_type == JobTypes.JOB_INIT.name or job.job_type == JobTypes.JOB_SPLIT.name

def test_optimizer_schedules_training_after_initialization(initialization_payload, init_dmlresult_obj, split_dmlresult_obj):
    optimizer = FederatedAveragingOptimizer(initialization_payload)
    initial_weights = init_dmlresult_obj.results['weights']
    init_dmlresult_obj.job = init_dmlresult_obj.job.copy_constructor()
    split_dmlresult_obj.job = split_dmlresult_obj.job.copy_constructor()
    event_type, job_arr = optimizer.ask(RawEventTypes.JOB_DONE.name, init_dmlresult_obj)
    assert all(np.allclose(arr1, arr2) for arr1,arr2 in zip(optimizer.job.weights, initial_weights))    
    assert event_type == ActionableEventTypes.NOTHING.name
    event_type, job_arr = optimizer.ask(RawEventTypes.JOB_DONE.name, split_dmlresult_obj)
    assert event_type == ActionableEventTypes.SCHEDULE_JOBS.name
    for job in job_arr:
        assert job.job_type == JobTypes.JOB_TRAIN.name

def test_optimizer_schedules_communication_after_training(initialization_payload, train_dmlresult_obj):
    optimizer = FederatedAveragingOptimizer(initialization_payload)
    trained_weights = train_dmlresult_obj.results['weights']
    train_dmlresult_obj.job = train_dmlresult_obj.job.copy_constructor()
    event_type, job_arr = optimizer.ask(RawEventTypes.JOB_DONE.name, train_dmlresult_obj)
    assert all(np.allclose(arr1, arr2) for arr1,arr2 in zip(optimizer.job.weights, trained_weights))
    assert event_type == ActionableEventTypes.SCHEDULE_JOBS.name
    for job in job_arr:
        assert job.job_type == JobTypes.JOB_COMM.name
