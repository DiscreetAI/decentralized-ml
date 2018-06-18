import pandas as pd
import os
import shutil

class TransformedNotFoundError(FileNotFoundError):
    def __init__(self):
        FileNotFoundError.__init__(self, "No transformed data found. Did you make sure to transform the data first?")

class DatasetManager():
    def __init__(self, raw_filepath, name):
        self.rfp = raw_filepath
        self.name = name
        self.tfp = None

    def transform_data(self, transform_function):
        raw_data = self.get_raw_data()
        transformed_data = transform_function(raw_data)
        self.tfp = os.path.join(self.rfp, "transformed")
        if not os.path.exists(self.tfp):
            os.makedirs(self.tfp)
        transformed_data.to_csv(os.path.join(self.tfp, self.name), index=False)

    def get_raw_data(self):
        return pd.read_csv(os.path.join(self.rfp, self.name))

    def get_transformed_data(self):
        if self.tfp:
            return pd.read_csv(os.path.join(self.tfp, self.name))
        else:
            raise TransformedNotFoundError()
    
    def reset(self):
        if self.tfp:
            shutil.rmtree(self.tfp)
            self.tfp = None
        else:
            print("No transformed data to delete")


