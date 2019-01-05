import pandas as pd


class Dataset(object):
    """
    Dataset

    - Stores details about a dataset as an object for modularity.
    - Similar to the DMLObject/DMLResult in the UNIX Service.
    """
    def __init__(self, item):
        """
        Set the uuid, sample, and metadata attributes of the object

        item is a (key, value) pair where the key is the uuid of the dataset
        and value is a tuple containing the sample and metadata jsons of the
        dataset.
        """
        uuid, data_tuple = item
        sample, metadata = data_tuple
        sample, metadata = pd.read_json(sample), pd.read_json(metadata)
        self.uuid = uuid
        self.sample = sample
        self.metadata = metadata