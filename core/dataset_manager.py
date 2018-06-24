import numpy as np
import pandas as pd
import os
import shutil
import logging


logging.basicConfig(level=logging.INFO,
                    format='[DatasetManager] %(asctime)s %(levelname)s %(message)s')
                    
class TransformedNotFoundError(Exception):
    '''
    TransformedNotFoundError

    Just a customized exception for when the caller tries to access transformed data that doesn't exist.
    '''
    def __init__(self):
        Exception.__init__(self, "No transformed data found. Did you make sure to transform the data first?")

class DatasetManager():
    '''
    DatasetManager


    IMPORTANT: ALL FILEPATHS ARE ABSOLUTE FILEPATHS. If you have a relative filepath, simply:
        
        import os
        absolute_path = os.path.abspath(relative_path)
    
    to get the absolute filepath.


    This class takes in an filepath to raw data upon initialization. Some functionalities include:

        1. Taking in a transform function, transforming the data, and putting this transformed data 
        in a new directory within the same directory as the raw data

        2. Returning the raw data and transformed data (if it exists)

        3. Resetting, or removing the folder of transformed data (as if the initial transform never took place)

    Each instance corresponds to a set of raw data and its corresponding transformed data (if it exists).
    '''
    def __init__(self, raw_filepath):
        '''
        Take in an filepath to the raw data, no filepath to transformed exists yet
        '''
        print(raw_filepath)
        if not os.path.isdir(raw_filepath):
            raise NotADirectoryError()
        self.rfp = raw_filepath
        self.tfp = None

    def transform_data(self, transform_function):
        '''
        Taking in a transform function, transforming the data, and putting this transformed data 
        in a new directory (called 'transformed') in the same directory as the raw data
        '''
        #1. Extracts all of the raw data from raw data filepath
        raw_data = self.get_raw_data() 

        #2. Creates a new directory in raw data filepath called 'transformed'
        self.tfp = os.path.join(self.rfp, "transformed")
        if not os.path.exists(self.tfp):
            os.makedirs(self.tfp)
            
        #3. Tranforms data using provided transform function and puts data in 'transformed
        transform_dict = {} 
        for name,data in raw_data.items():
            transformed_data = transform_function(data) 
            transformed_data.to_csv(os.path.join(self.tfp, name), index=False)

        assert os.path.isdir(os.path.join(self.rfp, 'transformed'))

    def get_raw_data(self):
        '''
        Extracts all raw data from raw data filepath. Assumes filepath contains csv
        files. Returns where each (key, value) represents a csv file. Each key is the
        filename of the csv (i.e. key.csv) and each value is a DataFrame of the actual data.
        '''
        raw_dict = {}
        for file in os.listdir(self.rfp): 
            if file[-4:] == '.csv':
                data = pd.read_csv(os.path.join(self.rfp, file))
                raw_dict[file] = data     
        return raw_dict

    def get_transformed_data(self):
        '''
        Extracts all transformed data from transform data filepath. 
        
        If filepath exists, assumes filepath contains csvfiles. Returns where each (key, value) 
        represents a csv file. Each key is the filename of the csv (i.e. key.csv) and each value 
        is a DataFrame of the actual data.

        If filepath does not exist, throws TransformedNotFoundError
        '''
        if self.tfp:
            transform_dict = {}
            for file in os.listdir(self.tfp): 
                if file[-4:] == '.csv':
                    data = pd.read_csv(os.path.join(self.tfp, file))
                    transform_dict[file] = data     
            return transform_dict
        else:
            raise TransformedNotFoundError()
    
    def reset(self):
        '''
        Resets class as though transformed data never existed.

        If transform data filepath exists, then delete directory and all files in that directory.
        Update filepath to None (transform data filepath no longer exists)

        If transform data filepath does not exist (there was no transformed data to begin with), 
        do nothing.
        '''
        if self.tfp:
            shutil.rmtree(self.tfp)
            self.tfp = None
        assert not os.path.isdir(os.path.join(self.rfp, 'transformed')) 


