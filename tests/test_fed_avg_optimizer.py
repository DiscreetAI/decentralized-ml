import tests.context

import pytest
import numpy as np

from tests.testing_utils import make_initialize_job, make_train_job
from tests.testing_utils import make_serialized_job, make_model_json
from tests.testing_utils import make_hyperparams
from core.utils.enums import JobTypes, RawEventTypes, ActionableEventTypes
from core.fed_avg_optimizer import FederatedAveragingOptimizer
from core.runner import DMLRunner
from core.configuration import ConfigurationManager

@pytest.fixture
def config_manager():
    config_manager = ConfigurationManager()
    config_manager.bootstrap(
        config_filepath='tests/artifacts/fed_avg_optimizer/configuration.ini'
    )
    return config_manager

@pytest.fixture
def initialization_payload():
    return {
        "optimizer_params": {"listen_bound": 2, "listen_iterations": 0},
        "serialized_job": make_serialized_job()
    }

@pytest.fixture
def init_dmlresult_obj(config_manager):
    runner = DMLRunner(config_manager)
    initialize_job = make_initialize_job(make_model_json())
    result = runner.run_job(initialize_job)
    return result

@pytest.fixture
def train_dmlresult_obj(config_manager, init_dmlresult_obj):
    runner = DMLRunner(config_manager)
    initialize_job = make_initialize_job(make_model_json())
    initial_weights = init_dmlresult_obj.results['weights']
    train_job = make_train_job(make_model_json(), initial_weights, make_hyperparams())
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
    event_type, job = optimizer.kickoff()
    assert event_type == ActionableEventTypes.SCHEDULE_JOB.name
    assert job.job_type == JobTypes.JOB_INIT.name


def test_optimizer_schedules_training_after_initialization(initialization_payload, init_dmlresult_obj):
    optimizer = FederatedAveragingOptimizer(initialization_payload)
    event_type, job = optimizer.ask(RawEventTypes.JOB_DONE.name, init_dmlresult_obj)
    initial_weights = init_dmlresult_obj.results['weights']
    assert all([np.count_nonzero(arr)==0 for arr in np.subtract(optimizer.job.weights, initial_weights)])
    assert event_type == ActionableEventTypes.SCHEDULE_JOB.name
    assert job.job_type == JobTypes.JOB_TRAIN.name


def test_optimizer_schedules_communication_after_training(initialization_payload, train_dmlresult_obj):
    optimizer = FederatedAveragingOptimizer(initialization_payload)
    event_type, job = optimizer.ask(RawEventTypes.JOB_DONE.name, train_dmlresult_obj)
    trained_weights = train_dmlresult_obj.results['weights']
    assert all([np.count_nonzero(arr)==0 for arr in np.subtract(optimizer.job.weights, trained_weights)])
    assert event_type == ActionableEventTypes.SCHEDULE_JOB.name
    assert job.job_type == JobTypes.JOB_COMM.name
