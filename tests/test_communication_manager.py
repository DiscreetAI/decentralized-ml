import tests.context

import pytest
import time

from core.communication_manager import CommunicationManager
from core.runner                import DMLRunner
from core.scheduler             import DMLScheduler
from core.configuration         import ConfigurationManager
from tests.testing_utils        import make_initialize_job, make_model_json
from tests.testing_utils        import make_serialized_job, serialize_job
from core.utils.enums           import RawEventTypes


config_manager = ConfigurationManager()
config_manager.bootstrap(
    config_filepath='tests/artifacts/communication_manager/configuration.ini'
)

def test_communication_manager_can_initialize_and_train_model():
    """
    Integration test that checks that the Communication Manager can initialize,
    train, (and soon communicate) a model.

    NOTE: This should be renamed after the COMM PR.

    This is everything that happens in this test:

    (1) Communication Manager receives the packet it's going to receive from
        BlockchainGateway
    (2) Communication Manager gives packet to Optimizer
    (3) Optimizer tells Communication Manager to schedule an initialization job
    (4) Communication Manager schedules initialization job
    (5) Communication Manager receives DMLResult for initialization job from
        Scheduler
    (6) Communication Manager gives DMLResult to Optimizer
    (7) Optimizer updates its weights to initialized model
    (8) Optimizer tells Communication Manager to schedule a training job
    (9) Communication Manager schedules training job
    (10) Communication Manager receives DMLResult for training job from
         Scheduler
    (11) Communication Manager gives DMLResult to Optimizer
    (12) Optimizer updates its weights to trained weights

    NOTE: These next steps are not implemented yet! (They need the COMM PR.)
    (13) Optimizer tells Communication Manager to schedule a communication job
    (14) Communication Manager schedules communication job
    (15) Communication Manager receives DMLResult for communication job from
         Scheduler
    (16) Communication Manager gives DMLResult to Optimizer
    (17) TO BE DEFINED (COMM PR.)
    """
    communication_manager = CommunicationManager()
    scheduler = DMLScheduler(config_manager)
    communication_manager.configure(scheduler)
    scheduler.configure(communication_manager)
    new_session_event = {
        "key": None,
        "content": {
            "optimizer_params": {},
            "serialized_job": make_serialized_job()
        }
    }
    communication_manager.inform(
        RawEventTypes.NEW_SESSION.name,
        new_session_event
    )
    while len(scheduler.processed) == 0:
        scheduler.runners_run_next_jobs()
        time.sleep(0.1)
    while len(scheduler.processed) == 1:
        scheduler.runners_run_next_jobs()
        time.sleep(0.1)
    assert len(scheduler.processed) == 2


def test_communication_manager_can_be_initialized():
    """
    Very simple check. Checks if the Communication Manager can initialize.
    """
    communication_manager = CommunicationManager()
    assert communication_manager


def test_communication_manager_fails_if_not_configured():
    """
    Ensures that Communication Manager won't be able to function if it's not
    configured.
    """
    communication_manager = CommunicationManager()
    serialized_job = make_serialized_job()
    new_session_event = {
        "key": None,
        "content": {
            "optimizer_params": {},
            "serialized_job": serialized_job
        }
    }
    try:
        communication_manager.inform(
            RawEventTypes.NEW_SESSION.name,
            new_session_event
        )
        raise Exception("This should have raised an exception")
    except Exception as e:
        assert str(e) == "Communication Manager needs to be configured first!"


def test_communication_manager_creates_new_sessions():
    """
    Ensures that upon receiving an initialization job, the Communication Manager
    will make an optimizer.
    """
    communication_manager = CommunicationManager()
    scheduler = DMLScheduler(config_manager)
    communication_manager.configure(scheduler)
    scheduler.configure(communication_manager)
    serialized_job = make_serialized_job()
    new_session_event = {
        "key": None,
        "content": {
            "optimizer_params": {},
            "serialized_job": serialized_job
        }
    }
    communication_manager.inform(
        RawEventTypes.NEW_SESSION.name,
        new_session_event
    )
    assert communication_manager.optimizer


def test_communication_manager_can_inform_new_job_to_the_optimizer():
    """
    Ensures that Communication Manager can tell the optimizer of something,
    and that the job will transfer correctly.
    """
    communication_manager = CommunicationManager()
    scheduler = DMLScheduler(config_manager)
    communication_manager.configure(scheduler)
    scheduler.configure(communication_manager)
    true_job = make_initialize_job(make_model_json())
    serialized_job = serialize_job(true_job)
    new_session_event = {
        "key": None,
        "content": {
            "optimizer_params": {},
            "serialized_job": serialized_job
        }
    }
    communication_manager.inform(
        RawEventTypes.NEW_SESSION.name,
        new_session_event
    )
    optimizer_job = communication_manager.optimizer.job
    assert optimizer_job.weights == true_job.weights
    assert optimizer_job.job_type == true_job.job_type
    assert optimizer_job.serialized_model == true_job.serialized_model
    assert optimizer_job.framework_type == true_job.framework_type
    assert optimizer_job.hyperparams == true_job.hyperparams
    assert optimizer_job.label_column_name == true_job.label_column_name


# NOTE: The following are tests that we will implement soon.

# def test_communication_manager_can_parse_events_correctly(communication_manager):
#     """To be implemented."""
#     assert False, "Implement me!"


# def test_communication_manager_terminates_sessions():
#     """
#     Tests that the Communication Manager can terminate a session after setting it up.
#     """
#     communication_manager = CommunicationManager()
#     scheduler = DMLScheduler(config_manager, communication_manager)
#     communication_manager.configure(scheduler)
#     true_job = make_initialize_job(make_model_json())
#     serialized_job = serialize_job(true_job)
#     new_session_event = {
#         "key": None,
#         "content": {
#             "optimizer_params": {},
#             "serialized_job": serialized_job
#         }
#     }
#     communication_manager.inform(RawEventTypes.NEW_SESSION.name, new_session_event)
#     terminate_session_event = {
#         "key": None,
#         "content": {}
#     }
#     communication_manager.inform(RawEventTypes.NEW_INFO.name, terminate_session_event)
#     assert not communication_manager.optimizer
