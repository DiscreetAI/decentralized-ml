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
    count = 0
    for filename in os.listdir(dataset_path):
        if not filename.endswith(".csv"): continue
        full_path = os.path.join(dataset_path, filename)
        with open(full_path, 'r') as f:
            for line in f:
                count += 1
        count -= 1 #exclude header
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

def reverse_readline(filename, buf_size=8192):
    """
    A generator that returns the lines of a file in reverse order

    Obtained from: 
    https://stackoverflow.com/questions/2301789/read-a-file-in-reverse-order-using-python
    """
    with open(filename) as fh:
        segment = None
        offset = 0
        fh.seek(0, os.SEEK_END)
        file_size = remaining_size = fh.tell()
        while remaining_size > 0:
            offset = min(file_size, offset + buf_size)
            fh.seek(file_size - offset)
            buffer = fh.read(min(remaining_size, buf_size))
            remaining_size -= buf_size
            lines = buffer.split('\n')
            # the first line of the buffer is probably not a complete line so
            # we'll save it and append it to the last line of the next buffer
            # we read
            if segment is not None:
                # if the previous chunk starts right from the beginning of line
                # do not concact the segment to the last line of new chunk
                # instead, yield the segment first 
                if buffer[-1] is not '\n':
                    lines[-1] += segment
                else:
                    yield segment
            segment = lines[0]
            for index in range(len(lines) - 1, 0, -1):
                if len(lines[index]):
                    yield lines[index]
        # Don't yield None if the file was empty
        if segment is not None:
            yield segment

def _create_dataset_iterator(dataset_path, max_count, iter_type, batch_size, labeler):
    """
    Returns an iterator of batches of size B containing all features of the data.

    Assumes `dataset_path` is a path to a folder with multiple CSV files.

    NOTE: labeler is now a string that refers to a column name
    """
    assert iter_type in ['train', 'test'], "'iter_type' parameter is invalid."
    if iter_type == 'train':
        directories = os.listdir(dataset_path)
    elif iter_type == 'test':
        directories = reversed(os.listdir(dataset_path))

    count = 0
    num_batches = 0
    batch = []
    for filename in directories:
        if not filename.endswith(".csv"): continue
        full_path = os.path.join(dataset_path, filename)
        if iter_type == 'test':
            f = reverse_readline(full_path)
        else:
            f = open(full_path)
        next(iter(f)) #first line contains header, so ignore it
        for line in f:
            if len(batch) == batch_size:
                if batch_size == 1:
                    tup = batch[0]
                    yield (np.expand_dims(tup[0], axis=0), \
                        np.expand_dims(tup[1], axis=0))
                else:
                    num_batches += 1
                    X_list, y_list = list(), list()
                    for x, _ in batch: X_list.append(x)
                    for _, y in batch: y_list.append(y)
                    yield (np.array(X_list), np.array(y_list))
                batch = []
            if count >= max_count:
                return
            line = line.split(",")
            line = line[0:labeler] + line[labeler + 1:], line[labeler]
            batch.append(line)
            count += 1