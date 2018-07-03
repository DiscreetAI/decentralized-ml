import numpy as np
import pandas as pd
import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
#print(sys.path)
from core.dataset_manager import DatasetManager, TransformedNotFoundError, NoMetadataFoundError

def dsm_initialization_test(dsm, rfp):
    '''
    Check that DM instance has path to raw data and that path transformed data
    hasn't been made yet (since no transform has been done yet)
    '''
    assert dsm.rfp == rfp
    assert not dsm.tfp

def same_raw_data_test(dsm, expected_test1_raw, expected_test2_raw):
    '''
    Check get_raw_data actually returns the data in this directory
    '''
    raw_data = dsm.get_raw_data()
    actual_test1_raw = raw_data['test1.csv']
    actual_test2_raw = raw_data['test2.csv']
    assert expected_test1_raw.equals(actual_test1_raw)
    assert expected_test2_raw.equals(actual_test2_raw)

def transformation_happened_test(dsm, rfp):
    '''
    Check that a new directory in the raw data filepath called 'transformed' is made and
    the DM instance has the filepath to this new directory
    '''
    assert dsm.tfp == rfp + '/transformed'
    assert os.path.isdir(rfp + '/transformed')

def accurate_transform_test(dsm, expected_test1_transformed, expected_test2_transformed):
    '''
    Check that the data in this folder is the result of calling the transform function on 
    each csv in the raw data filepath
    '''
    transform_dsm = dsm.get_transformed_data()
    keys = list(transform_dsm.keys())
    actual_test1_transformed = transform_dsm[keys[0]].round(3)
    actual_test2_transformed = transform_dsm[keys[1]].round(3)
    assert expected_test1_transformed.equals(actual_test1_transformed) or \
        expected_test1_transformed.equals(actual_test2_transformed)
    assert expected_test2_transformed.equals(actual_test2_transformed) or \
        expected_test2_transformed.equals(actual_test1_transformed)

def reset_test(dsm, rfp):
    '''
    Check the raw data filepath exists, the transformed data filepath doesn't, and the 'transformed' folder
    is gone from the raw data directory
    '''
    assert dsm.rfp == rfp
    assert not dsm.tfp
    assert not os.path.isdir(rfp + '/transformed')

def transform_not_found_exception_test(dsm):
    '''
    After resetting, check to make sure that getting the transformed data is impossible
    '''
    try:
        transformed = dsm.get_transformed_data() 
        assert False
    except TransformedNotFoundError:
        pass
    

def test_end_to_end():
    #Sample transform function (takes dataframe, returns dataframe)
    def do_nothing(df):
        return df

    rfp = os.path.join(currentdir, 'artifacts/dataset_manager_test_data')  
    expected_test1_raw = pd.read_csv(rfp + '/test1/test1.csv')
    expected_test2_raw = pd.read_csv(rfp + '/test2/test2.csv')
    expected_test1_transformed = do_nothing(expected_test1_raw).round(3)
    expected_test2_transformed = do_nothing(expected_test2_raw).round(3)

    dsm = DatasetManager(rfp)
    dsm_initialization_test(dsm, rfp)

    raw_dsm = dsm.get_raw_data()
    same_raw_data_test(dsm, expected_test1_raw, expected_test2_raw)
    
    dsm.transform_data(do_nothing)
    transformation_happened_test(dsm, rfp)
    accurate_transform_test(dsm, expected_test1_transformed, expected_test2_transformed)

    dsm.reset()
    reset_test(dsm, rfp)
    #dsm.post_dataset("my_test")

def test_bad_rfp():
    try:
        dsm = DatasetManager("no/file/directory/here")
        assert False
    except NotADirectoryError:
        pass

def test_bad_metadata_post():
    try:
        rfp = os.path.join(currentdir, 'artifacts/dataset_manager_test_data') 
        dsm = DatasetManager(rfp)
        dsm.post_dataset_with_md("my_test") 
        assert False
    except NoMetadataFoundError:
        pass
 



