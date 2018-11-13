import numpy as np
import pandas as pd
import os
import sys
import inspect
import tests.context
import pytest
import shutil
from core.configuration import ConfigurationManager
from core.dataset_manager import DatasetManager


@pytest.fixture
def bad_config_manager_format():
    config_manager = ConfigurationManager()
    config_manager.bootstrap(
        config_filepath='tests/artifacts/dataset_manager/configuration2.ini'
    )
    return config_manager

@pytest.fixture
def bad_config_manager_header():
    config_manager = ConfigurationManager()
    config_manager.bootstrap(
        config_filepath='tests/artifacts/dataset_manager/configuration3.ini'
    )
    return config_manager

def test_no_header(bad_config_manager_header):
    """
    Test that DSM invalidates dataset with no header.
    """
    error_message = ("No header has been provided in file {file} in folder "
                     "{folder}")
    error_message = error_message.format(
                        file='test1.csv',
                        folder='test1',
                    )
    try:
        dsm = DatasetManager(bad_config_manager_header)
        raise Exception("Error should have been thrown for lack of header")
    except AssertionError as e:
        assert str(e) == error_message, "Wrong assertion was thrown!"

def test_bad_format(bad_config_manager_format):
    """
    Test that DSM invalidates dataset with invalid CSV format.
    """
    format_message = ("The file {file} in folder {folder} was improperly "
                      "formatted. Please refer to the following error "
                      "message from pandas for more information: {message}")
    format_message = format_message.format(
                        file='test1.csv',
                        folder='test1',
                        message='list index out of range'
                     )                  
    try:
        dsm = DatasetManager(bad_config_manager_format)
        raise Exception("Error should have been thrown for bad format")
    except Exception as e:
        assert str(e) == format_message, "Wrong assertion was thrown!"

'''
uncomment when node is running

def test_bad_metadata_post():
    try:
        rfp = os.path.join(currentdir, 'artifacts/dataset_manager_test_data')
        dsm = DatasetManager(rfp)
        dsm.post_dataset_with_md("my_test")
        assert False
    except NoMetadataFoundError:
        pass

'''
