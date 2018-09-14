import tests.context

import time
import logging
import os
import pytest
import numpy as np

from custom.keras               import get_optimizer
from models.keras_perceptron    import KerasPerceptron
from core.utils.dmljob          import DMLJob
from core.scheduler             import DMLScheduler
from core.configuration         import ConfigurationManager


config_manager = ConfigurationManager()
config_manager.bootstrap(
    config_filepath='tests/artifacts/configuration.ini'
)
scheduler = DMLScheduler(config_manager)

def make_model_json():
    m = KerasPerceptron(is_training=True)
    model_architecture = m.model.to_json()
    model_optimizer = get_optimizer(m.model)
    model_json = {
        "architecture": model_architecture,
        "optimizer": model_optimizer
    }
    return model_json


def make_initialize_job(model_json):
    initialize_job = DMLJob(
        "initialize",
        model_json,
        "keras"
    )
    return initialize_job


def test_dmlscheduler_sanity():
    """ Check that the scheduling/running functionality is maintained. """
    model_json = make_model_json()
    initialize_job = make_initialize_job(model_json)
    scheduler.add_job(initialize_job)
    scheduler._runners_run_next_jobs()
    while not scheduler.processed:
        scheduler._runners_run_next_jobs()
    initial_weights = scheduler.processed.pop(0)
    assert type(initial_weights) == list
    assert type(initial_weights[0]) == np.ndarray
    

def test_dmlscheduler_arbitrary_scheduling():
    """ Manually schedule events and check that all jobs are completed """
    scheduler = DMLScheduler.get_instance()
    scheduler.reset()
    model_json = make_model_json()
    first = make_initialize_job(model_json)
    second = make_initialize_job(model_json)
    scheduler.add_job(first)
    scheduler.add_job(second)
    while len(scheduler.processed) == 0:
        scheduler._runners_run_next_jobs()
    third = make_initialize_job(model_json)
    fourth = make_initialize_job(model_json)
    scheduler.add_job(third)
    scheduler.add_job(fourth)
    while len(scheduler.processed) < 4:
        scheduler._runners_run_next_jobs()
    fifth = make_initialize_job(model_json)
    scheduler.add_job(fifth)
    while len(scheduler.processed) < 5:
        scheduler._runners_run_next_jobs()
    assert len(scheduler.processed) == 5
    while scheduler.processed:
        initial_weights = scheduler.processed.pop(0)
        assert type(initial_weights) == list
        assert type(initial_weights[0]) == np.ndarray


def test_dmlscheduler_cron():
    """ Test that scheduler works """
    scheduler = DMLScheduler.get_instance()
    scheduler.reset()
    model_json = make_model_json()
    for _ in range(3):
        model_json = make_model_json()
        initialize_job = make_initialize_job(model_json)
        scheduler.add_job(initialize_job)
    scheduler._start_cron(period = 0.05)
    time.sleep(5)
    scheduler._stop_cron()
    assert len(scheduler.processed) == 3
    while scheduler.processed:
        initial_weights = scheduler.processed.pop(0)
        assert type(initial_weights) == list
        assert type(initial_weights[0]) == np.ndarray
