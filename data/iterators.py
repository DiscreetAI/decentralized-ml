import os

import numpy as np
import pandas as pd
import keras
import warnings


def count_datapoints(dataset_path):
    """
    Counts and returns the number of datapoints in the `dataset_path` directory.
    One line in a file inside the directory is equivalent to one datapoint.
    """
    assert os.path.isdir(dataset_path), "Dataset path is invalid."

    count = 0
    for filename in os.listdir(dataset_path):
        if not filename.endswith(".csv"): continue
        full_path = os.path.join(dataset_path, filename)
        with open(full_path, 'r') as f:
            for line in f:
                count += 1
        count -= 1 #exclude header
    return count

def create_mapping(count, split=0.8):
    """
    Randomly assign each datapoint to be in the training set or test set.

    Args:
        count - total number of datapoints
        split - proportion of datapoint to be in training set

    Returns:
        mapping - dictionary mapping each datapoint to train or test

    """
    train_data_points = np.random.choice(count, int(split*count), False)
    mapping = {}
    for i in range(count):
        mapping[i] = 'train' if i in train_data_points else 'test'
    return mapping

def create_train_dataset_iterator(dataset_path, count, mapping, split=0.8, batch_size=1, \
    labeler=None, infinite=True):
    """
    Returns an iterator of batches of size B containing all features of the data.

    Assumes `dataset_path` is a path to a folder with multiple CSV files.
    """
    if infinite:
        while True:
            yield from _create_dataset_iterator(dataset_path, count*split, mapping, \
                "train", batch_size, labeler)
    else:
        yield from _create_dataset_iterator(dataset_path, count*split, mapping, \
            "train", batch_size, labeler)

def create_test_dataset_iterator(dataset_path, count, mapping, split=0.2, batch_size=1, \
    labeler=None, infinite=True):
    """
    Returns an iterator of batches of size B containing all features of the data.

    Assumes `dataset_path` is a path to a folder with multiple CSV files.
    """
    if infinite:
        while True:
            yield from _create_dataset_iterator(dataset_path, count*split, mapping, \
                "test", batch_size, labeler)
    else:
        yield from _create_dataset_iterator(dataset_path, count*split, mapping, \
            "test", batch_size, labeler)

def _create_dataset_iterator(dataset_path, max_count, mapping, iter_type, batch_size, labeler):
    """
    Returns an iterator of batches of size B containing all features of the 
    data. If batch_size > max_count, then the datapoints for the dataset 
    will be single batch of data (the iterator only iterates over one item.

    Assumes `dataset_path` is a path to a folder with multiple CSV files.

    NOTE: labeler is now an integer that refers to the index of the column
    """
    assert iter_type in ['train', 'test'], "'iter_type' parameter is invalid."
    assert os.path.isdir(dataset_path), "Dataset path is invalid."
    assert batch_size > 0, "Invalid batch size provided."
    directories = os.listdir(dataset_path)
    count = 0
    index = -1 # code is cleaner if we increment at start of loop
    batch = []
    for filename in directories:
        if not filename.endswith(".csv"): continue
        full_path = os.path.join(dataset_path, filename)
        f = open(full_path)
        next(iter(f)) #first line contains header, so ignore it
        for line in f:
            index += 1

            # If we iterated through enough data points for this set, stop. 
            if count >= max_count: break

            # Don't add datapoint if it doesn't belong in this set
            if mapping[index] != iter_type: continue

            # When batch is full, yield it, then empty it
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
            
            # Add datapoint to batch
            line = line.split(",")
            assert labeler >= 0 and labeler < len(line), "Labeler is out of bounds."
            line = line[0:labeler] + line[labeler + 1:], line[labeler]
            batch.append(line)
            count += 1

    # After we have iterated through enough data points for this set, if there
    # are still datapoints in the batch, yield the batch.
    if batch:
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