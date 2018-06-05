import os

import numpy as np

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
    """
    assert iter_type in ['train', 'test'], "'iter_type' parameter is invalid."
    if iter_type == 'train':
        directories = os.listdir(dataset_path)
    elif iter_type == 'test':
        directories = reversed(os.listdir(dataset_path))

    count = 0
    for filename in directories:
        if not filename.endswith(".csv"): continue
        full_path = os.path.join(dataset_path, filename)
        with open(full_path, 'r') as f:
            batch = []
            for line in f:
                if count >= max_count:
                    return
                if len(batch) == batch_size:
                    if batch_size == 1:
                        tup = batch[0]
                        yield (np.expand_dims(tup[0], axis=0), \
                            np.expand_dims(tup[1], axis=0))
                    else:
                        X_list, y_list = list(), list()
                        for x, _ in batch: X_list.append(x)
                        for _, y in batch: y_list.append(y)
                        yield (np.array(X_list), np.array(y_list))
                    batch = []
                line = labeler(line) if labeler else line
                batch.append(line)
                count += 1
