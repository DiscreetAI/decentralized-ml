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

def accurate_transform_test(dsm, expected_test_transformed, split):
    '''
    Check that the data in this folder is the result of calling the transform function on
    each csv in the raw data filepath
    '''
    transform_dsm = dsm.get_transformed_data()
    keys = list(transform_dsm.keys())
    train = transform_dsm['train']
    test = transform_dsm['test']
    count = len(expected_test_transformed)
    assert len(train) == int(split * count)
    assert len(test) == int((1 - split) * count)
    actual_test_transformed = train.append(test)
    actual_test_transformed = actual_test_transformed.reset_index(drop=True)
    merged_data = pd.merge(
        actual_test_transformed,
        expected_test_transformed,
        on = ['a', 'b', 'c'],
        how = 'inner'
    )
    assert len(actual_test_transformed) == count
    assert len(merged_data) == count

def clean_up_test(dsm, rfp):
    '''
    Check the raw data filepath exists, the transformed data filepath doesn't, and the 'transformed' folder
    is gone from the raw data directory
    '''
    assert dsm.rfp == rfp
    assert dsm.tfp == None
    assert not os.path.isdir(rfp + '/transformed')

def test_end_to_end(config_manager):
    #Sample transform function (takes dataframe, returns dataframe)
    def drop_duplicates(df):
        return df.drop_duplicates()
    
    rfp = 'tests/artifacts/dataset_manager/dataset_manager_test_data'
    tfp = 'tests/artifacts/dataset_manager/dataset_manager_test_data/transformed'
    expected_test1_raw = pd.read_csv(rfp + '/test1/test1.csv')
    expected_test2_raw = pd.read_csv(rfp + '/test2/test2.csv')
    combined_raw = expected_test1_raw.append(expected_test2_raw)
    expected_test_transformed = drop_duplicates(combined_raw).reset_index(drop=True)
    dsm = DatasetManager(config_manager)
    dsm.clean_up()
    dsm_initialization_test(dsm, rfp)
    same_raw_data_test(dsm, expected_test1_raw, expected_test2_raw)
    dsm.split_and_transform_data(drop_duplicates, 0.75)
    accurate_transform_test(dsm, expected_test_transformed, 0.75)
    dsm.clean_up()
    clean_up_test(dsm, rfp) #leave commented out until we figure out reset
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
