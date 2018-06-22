import keras
import numpy as np


def mnist_labeler(line):
    """
    Returns an (X, y) tuple from a line of the MNIST CSV files, where X is a
    (784, 1) numpy array and y is a scalar.

    The input is of the format `label, pix-11, pix-12, pix-13, ...`.
    """
    line = line.split(',')
    X = np.array(line[1:], dtype=np.uint8).reshape((784,))
    y = int(line[0])
    assert X.size == 784, "Dimension of `X` is not 784."
    assert 0 <= y <= 9, "`y` is not between 0 and 9."
    y = keras.utils.to_categorical(y, num_classes=10)
    return (X, y)

def lstm_labeler(line, apt_num = 1):

    line = line.split(',')
    y = float(line[apt_num])
    del line[apt_num]
    X = line
    return (X, y)