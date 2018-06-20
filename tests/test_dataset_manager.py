import numpy as np
import pandas as pd
import os
from DatasetManager import DatasetManager

def standardize_df(df):
    def standardize(x):
        return (x-np.mean(x))/np.std(x)
    return df.apply(standardize)


dsm = DatasetManager('test', 'test.csv')
raw = dsm.get_raw_data()
print("Raw Data:")
print(raw)
print()
print("Printing directory of test")
print(os.listdir("test"))
print()

dsm.transform_data(standardize_df)
transformed = dsm.get_transformed_data()
print("Transformed Data")
print(transformed)
print()
print("Printing directory of test")
print(os.listdir("test"))
print()


print("Called reset")
dsm.reset()
print("Trying to get transformed data:")
transformed = dsm.get_transformed_data() # should error
