import shutil
import logging
import datetime
import string
import random
import os
import yaml
import uuid

import numpy as np
import pandas as pd
import ipfsapi

import core.utils.context
from core.configuration import ConfigurationManager
from core.blockchain.blockchain_utils import setter


logging.basicConfig(level=logging.INFO,
                format='[DatasetManager] %(asctime)s %(levelname)s %(message)s')

class DatasetManager():
    """
    Dataset Manager

    This class takes in an filepath to raw data upon initialization.
    Some functionalities include:

        1. Validating data.
        2. TODO: Detecting changes in data 
        3. TODO: Validating data after changes, validating only new data?

    Each instance corresponds to a set of raw data. The directory should look 
    something like this:

    main/
        dataset1/
            dataset1.csv
        dataset2/
            dataset2.csv

    The Dataset Manager will be initialized in the Bootstrapper. 
    """

    def __init__(self, config_manager):
        """
        Take in an filepath to the raw data.

        For now, throw an exception if a valid dataset path is not provided.

        TODO: In the event of a invalid dataset path, log a useful message 
        for the user and don't terminate the service
        """
        config = config_manager.get_config()
        raw_filepath = config['GENERAL']['dataset_path']
        assert os.path.isdir(raw_filepath), "The dataset filepath provided is not valid."
        self._raw_filepath = raw_filepath
        self._mappings = None
        self._validate_data()
        self._host = config.get("BLOCKCHAIN", "host")
        self._ipfs_port = config.getint("BLOCKCHAIN", "ipfs_port")
        self._port = config.getint("BLOCKCHAIN", "http_port")
        self._timeout = config.getint("BLOCKCHAIN", "timeout")
        try:
            self.client = ipfsapi.connect(self._host, self._ipfs_port)
        except Exception as e:
            logging.info("IPFS daemon not started, got: {0}".format(e))
            raise(e)

    def _validate_data(self):
        """
        Validate all raw data. As of now, checks that:
            1. Each dataset has a header. Assumes column names are always
               string. NOTE: if data is also string, then it is impossible
               to tell whether file has header or not.
            2. Each dataset is in a valid CSV format. pandas already
               performs this validation when it reads in CSV files, so just
               return the error from pandas if reading fails.
        """
        format_message = ("The file {file} in folder {folder} was improperly "
                          "formatted. Please refer to the following error "
                          "message from pandas for more information: {message}")
        header_message = ("No header has been provided in file {file} in "
                          "folder {folder}")
        for folder in os.listdir(self._raw_filepath):
            folder_path = os.path.join(os.path.abspath(self._raw_filepath), folder)
            if not os.path.isdir(folder_path): continue
            files = os.listdir(folder_path)
            for file in files:
                if not file.endswith(".csv"): continue
                if file[:2] == 'md': continue
                file_path = os.path.join(folder_path, file)
                try:
                    dataset = pd.read_csv(file_path, index_col=False)
                except Exception as e:
                    logging.error(str(e))
                    raise Exception(
                        format_message.format(
                            file=file,
                            folder=folder,
                            message=str(e)
                        )
                    )
                is_str = lambda c: not c.replace('.','',1).isdigit()
                assert all([is_str(c) for c in dataset.columns]), \
                    header_message.format(
                        file=file,
                        folder=folder
                    )

    def get_mappings(self):
        """
        Returns the dataset mappings.
        """
        if not self._mappings:
            raise Exception("Dataset Manager needs to be bootstrapped first.")
        return self._mappings

    def bootstrap(self):
        """
        Check if datasets.yaml exists. If so, load it into the class (if it
        hasn't been already). Otherwise, call _create_dataset_mappings

        Returns True if mappings had to be created, and False otherwise 
        (used for testing).
        """
        mapping_filepath = os.path.join(self._raw_filepath, "datasets.yaml")
        if os.path.isfile(mapping_filepath):
            if not self._mappings:
                with open(mapping_filepath, "r") as f:
                    self._mappings = yaml.load(f)
            return False
        else:
            self._create_dataset_mappings(mapping_filepath)
            return True
        
    def _create_dataset_mappings(self, mapping_filepath):
        """
        mapping_filepath is the filepath where datasets.yaml is created, which
        is <raw_filepath>/datasets.yaml.

        For each dataset folder in the raw_filepath, generate a random string
        using uuid and add a (key, value) pair to a dictionary such that the 
        random string is key and the dataset folder name is the value. Store
        the dictionary in _mappings and in a yaml file at mapping_filepath.

        Ultimately, we are assigning identifiers for each dataset.
        """
        mappings = {}
        for folder in os.listdir(self._raw_filepath):
            encoding = str(uuid.uuid4())
            mappings[encoding] = folder
        self._mappings = mappings
        with open(mapping_filepath, "w") as f:
            f.write(yaml.dump(mappings))

    def check_key_length(self, key):
        """
        Keys for datasets can only be at most 30 characters long.
        """
        if len(key) > 30:
            raise InvalidKeyError(key)

    def post_dataset_with_md(self, name):
        """
        Post samples of datasets on blockchain along with provided metadata
        under the provided name as the key

        IMPORTANT: NOT FINISHED DEBUGGING, DO NOT USE
        """
        filepath = self._raw_filepath
        self.check_key_length(name)
        value = {}
        folders = []
        for file in os.listdir(filepath):
            if os.path.isdir(os.path.join(os.path.abspath(filepath), file)):
                folders.append(file)
        for folder in folders:
            folder_dict = {}
            folder_path = os.path.join(os.path.abspath(filepath), folder)
            files = os.listdir(folder_path)
            for file in files:
                if file[:2] == 'md':
                    file_path = os.path.join(folder_path, file)
                    metadata = pd.read_csv(file_path)
                    folder_dict['md'] = metadata.to_json()
                else:
                    file_path = os.path.join(folder_path, file)
                    dataset = pd.read_csv(file_path)
                    sample = dataset.sample(frac=0.1)
                    folder_dict['ds'] = sample.to_json()
            if 'md' not in folder_dict:
                raise NoMetadataFoundError(folder)
            value[folder] = folder_dict
        receipt = setter(client=self.client, key=name, value=value, port=self.port)

    def post_dataset(self, name):
        """
        Post samples of datasets on blockchain with automatically generated
        metadata under provided name as the key

        IMPORTANT: NOT FINISHED DEBUGGING, DO NOT USE
        """
        filepath = self._raw_filepath
        self.check_key_length(name)
        value = {}
        folders = []
        for file in os.listdir(filepath):
            if os.path.isdir(os.path.join(os.path.abspath(filepath), file)):
                folders.append(file)
        for folder in folders:
            folder_dict = {}
            folder_path = os.path.join(os.path.abspath(filepath), folder)
            file = list(os.listdir(folder_path))[0]
            file_path = os.path.join(folder_path, file)
            dataset = pd.read_csv(file_path)
            md = pd.DataFrame(dataset.describe())
            sample = dataset.sample(frac=0.1)
            folder_dict['ds'] = sample.to_json()
            folder_dict['md'] = md.to_json()
            value[folder] = folder_dict
        receipt = setter(client=self.client, key=name, value=value, port=self.port)
