"""TODO: Need to make it into pytest test (@neel)"""

# import numpy as np
# import pandas as pd
# import os
# import sys
# sys.path.append('../core')
# #print(sys.path)
# from dataset_manager import DatasetManager, TransformedNotFoundError
#
# '''
# Function for DatasetManager (DM for short)
#
# Might need to be changed when a proper test framework is introduced.
# '''
# def testDatasetManager():
#     #Sample transform function (takes dataframe, returns dataframe)
#     def standardize_df(df):
#         def standardize(x):
#             return (x-np.mean(x))/np.std(x)
#         return df.apply(standardize)
#
#     #Check that DM instance has path to raw data and that path transformed data
#     # hasn't been made yet (since no transform has been done yet)
#     rfp = os.path.abspath('artifacts/dataset_manager_test_data')
#     dsm = DatasetManager(rfp)
#     assert dsm.rfp == rfp
#     assert not dsm.tfp
#
#     #Check get_raw_data actually returns the data in this directory
#     raw_dsm = dsm.get_raw_data()
#     assert raw_dsm['test.csv'].equals(pd.read_csv(rfp + '/test/test.csv')) and raw_dsm['test2.csv'].equals(pd.read_csv(rfp + '/test2/test2.csv'))
#
#     #Check that a new directory in the raw data filepath called 'transformed' is made and
#     # the DM instance has the filepath to this new directory
#     dsm.transform_data(standardize_df)
#     assert dsm.tfp == rfp + '/transformed'
#     assert os.path.isdir(rfp + '/transformed')
#
#     #Check that the data in this folder is the result of calling the transform function on
#     # each csv in the raw data filepath
#     transform_dsm = dsm.get_transformed_data()
#     keys = list(transform_dsm.keys())
#     key1 = keys[0]
#     key2 = keys[1]
#     assert (transform_dsm[key1].round(3).equals(standardize_df(pd.read_csv(rfp + '/test/test.csv')).round(3)) or \
#            transform_dsm[key1].round(3).equals(standardize_df(pd.read_csv(rfp + '/test2/test2.csv')).round(3))) and \
#            (transform_dsm[key2].round(3).equals(standardize_df(pd.read_csv(rfp + '/test/test.csv')).round(3)) or \
#            transform_dsm[key2].round(3).equals(standardize_df(pd.read_csv(rfp + '/test2/test2.csv')).round(3)))
#
#     #After resetting, check to make sure that getting the transformed data is impossible
#     dsm.reset()
#     try:
#         transformed = dsm.get_transformed_data()
#         assert False
#     except TransformedNotFoundError:
#         pass
#
#     #Check the raw data filepath exists, the transformed data filepath doesn't, and the 'transformed' folder
#     # is gone from the raw data directory
#     assert dsm.rfp == rfp
#     assert not dsm.tfp
#     assert not os.path.isdir(rfp + '/transformed')
#
# #calling tests
# testDatasetManager()
