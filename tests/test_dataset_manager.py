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
def config_manager():
    config_manager = ConfigurationManager()
    config_manager.bootstrap(
        config_filepath='tests/artifacts/dataset_manager/configuration.ini'
    )
    return config_manager

def dsm_initialization_test(dsm, rfp):
    '''
    Check that DM instance has path to raw data and that path transformed data
    hasn't been made yet (since no transform has been done yet)
    '''
    assert dsm.rfp == rfp

def same_raw_data_test(dsm, expected_test1_raw, expected_test2_raw):
    '''
    Check _get_raw_data actually returns the data in this directory
    '''
    raw_data = dsm._get_raw_data()
    actual_test1_raw = raw_data['test1']
    actual_test2_raw = raw_data['test2']
    assert expected_test1_raw.equals(actual_test1_raw)
    assert expected_test2_raw.equals(actual_test2_raw)

def accurate_transform_test(dsm, expected_test1_transformed, expected_test2_transformed):
    '''
    Check that the data in this folder is the result of calling the transform function on
    each csv in the raw data filepath
    '''
    transform_dsm = dsm.get_transformed_data()
    keys = list(transform_dsm.keys())
    actual_test1_transformed = transform_dsm[keys[0]]
    actual_test2_transformed = transform_dsm[keys[1]]
    assert expected_test1_transformed.equals(actual_test1_transformed) or \
        expected_test1_transformed.equals(actual_test2_transformed)
    assert expected_test2_transformed.equals(actual_test2_transformed) or \
        expected_test2_transformed.equals(actual_test1_transformed)

def reset_test(dsm, rfp, tfp):
    '''
    Check the raw data filepath exists, the transformed data filepath doesn't, and the 'transformed' folder
    is gone from the raw data directory
    '''
    assert dsm.rfp == rfp
    assert dsm.tfp == tfp
    assert os.path.isdir(rfp + '/transformed')

def test_end_to_end(config_manager):
    #Sample transform function (takes dataframe, returns dataframe)
    def drop_duplicates(df):
        return df.drop_duplicates()

    rfp = 'tests/artifacts/dataset_manager/dataset_manager_test_data'
    tfp = 'tests/artifacts/dataset_manager/dataset_manager_test_data/transformed'
    expected_test1_raw = pd.read_csv(rfp + '/test1/test1.csv')
    expected_test2_raw = pd.read_csv(rfp + '/test2/test2.csv')
    expected_test1_transformed = drop_duplicates(expected_test1_raw).reset_index(drop=True)
    expected_test2_transformed = drop_duplicates(expected_test2_raw).reset_index(drop=True)

    dsm = DatasetManager(config_manager)
    dsm_initialization_test(dsm, rfp)
    same_raw_data_test(dsm, expected_test1_raw, expected_test2_raw)
    dsm.transform_data(drop_duplicates)
    accurate_transform_test(dsm, expected_test1_transformed, expected_test2_transformed)
    # dsm.reset()
    # reset_test(dsm, rfp, tfp) #leave commented out until we figure out reset
    shutil.rmtree(tfp)
    #dsm.post_dataset("my_test")

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
