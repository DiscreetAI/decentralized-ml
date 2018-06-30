import numpy as np
import pandas as pd
import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
#print(sys.path)
from core.dataset_manager import DatasetManager, TransformedNotFoundError

'''
Function for DatasetManager (DM for short)

Might need to be changed when a proper test framework is introduced.
'''
def test_dsm_initialization(dsm, rfp):
    '''
    Check that DM instance has path to raw data and that path transformed data
    hasn't been made yet (since no transform has been done yet)
    '''
    assert dsm.rfp == rfp
    assert not dsm.tfp

def test_same_raw_data(dsm, expected_test1_raw, expected_test2_raw):
    '''
    Check get_raw_data actually returns the data in this directory
    '''
    raw_data = dsm.get_raw_data()
    actual_test1_raw = raw_data['test1.csv']
    actual_test2_raw = raw_data['test2.csv']
    assert expected_test1_raw.equals(actual_test1_raw)
    assert expected_test2_raw.equals(actual_test2_raw)

def test_transformation_happened(dsm, rfp):
    '''
    Check that a new directory in the raw data filepath called 'transformed' is made and
    the DM instance has the filepath to this new directory
    '''
    assert dsm.tfp == rfp + '/transformed'
    assert os.path.isdir(rfp + '/transformed')

def test_accurate_transform(dsm, expected_test1_transformed, expected_test2_transformed):
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

def test_reset(dsm, rfp):
    '''
    Check the raw data filepath exists, the transformed data filepath doesn't, and the 'transformed' folder
    is gone from the raw data directory
    '''
    assert dsm.rfp == rfp
    assert not dsm.tfp
    assert not os.path.isdir(rfp + '/transformed')

def test_transform_not_found_exception(dsm):
    '''
    After resetting, check to make sure that getting the transformed data is impossible
    '''
    try:
        transformed = dsm.get_transformed_data() 
        assert False
    except TransformedNotFoundError:
        pass
    

def main_test():
    #Sample transform function (takes dataframe, returns dataframe)
    def standardize_df(df):
        def standardize(x):
            return (x-np.mean(x))/np.std(x)
        return df.apply(standardize)

    rfp = os.path.join(currentdir, 'artifacts/dataset_manager_test_data')  
    expected_test1_raw = pd.read_csv(rfp + '/test1/test1.csv')
    expected_test2_raw = pd.read_csv(rfp + '/test2/test2.csv')
    expected_test1_transformed = standardize_df(expected_test1_raw).round(3)
    expected_test2_transformed = standardize_df(expected_test2_raw).round(3)

    dsm = DatasetManager(rfp)
    test_dsm_initialization(dsm, rfp)

    raw_dsm = dsm.get_raw_data()
    test_same_raw_data(dsm, expected_test1_raw, expected_test2_raw)
    
    dsm.transform_data(standardize_df)
    test_transformation_happened(dsm, rfp)
    test_accurate_transform(dsm, expected_test1_transformed, expected_test2_transformed)

    dsm.reset()
    test_reset(dsm, rfp)
    #dsm.post_dataset("my_test")

#calling tests
main_test()