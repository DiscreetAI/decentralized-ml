import os

import numpy as np
import pandas as pd
import keras


def count_datapoints(dataset_path):
    """
    Counts and returns the number of datapoints in the `dataset_path` directory.
    One line in a file inside the directory is equivalent to one datapoint.
    """
    count = 0
    for filename in os.listdir(dataset_path):
        if not filename.endswith(".csv"): continue
        full_path = os.path.join(dataset_path, filename)
        with open(full_path, 'r') as f:
            for line in f:
                count += 1
    return count

def create_train_dataset_iterator(dataset_path, count, split=0.8, batch_size=1, \
    labeler=None, infinite=True):
    """
    Returns an iterator of batches of size B containing all features of the data.

    Assumes `dataset_path` is a path to a folder with multiple CSV files.
    """
    if infinite:
        while True:
            yield from _create_dataset_iterator(dataset_path, count*split, "train", \
                batch_size, labeler)
    else:
        yield from _create_dataset_iterator(dataset_path, count*split, "train", \
            batch_size, labeler)

def create_test_dataset_iterator(dataset_path, count, split=0.2, batch_size=1, \
    labeler=None, infinite=True):
    """
    Returns an iterator of batches of size B containing all features of the data.

    Assumes `dataset_path` is a path to a folder with multiple CSV files.
    """
    if infinite:
        while True:
            yield from _create_dataset_iterator(dataset_path, count*split, "test", \
                batch_size, labeler)
    else:
        yield from _create_dataset_iterator(dataset_path, count*split, "test", \
            batch_size, labeler)

def _create_dataset_iterator(dataset_path, max_count, iter_type, batch_size, labeler):
    """
    Returns an iterator of batches of size B containing all features of the data.

    Assumes `dataset_path` is a path to a folder with multiple CSV files.

    NOTE: labeler is now an integer that refers to the column index
    """
    assert iter_type in ['train', 'test'], "'iter_type' parameter is invalid."
    assert isinstance(labeler, str), "The labeler must be a string!"
    if iter_type == 'train':
        directories = os.listdir(dataset_path)
    elif iter_type == 'test':
        directories = reversed(os.listdir(dataset_path))

    num_batches = int(max_count/batch_size)
    total_points = int(max_count/batch_size) * batch_size
    for filename in directories:
        if not filename.endswith(".csv"): continue
        full_path = os.path.join(dataset_path, filename)
        file = pd.read_csv(full_path).head(total_points)
        assert labeler in file.columns, "Invalid column name for dataset"
        X, y = (file.drop(labeler, axis=1), pd.DataFrame(file[labeler]))
        X_split, y_split = np.split(X, num_batches), np.split(y, num_batches)
        for batch in zip(X_split,y_split):
            yield(batch)
