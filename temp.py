import pandas as pd 

data = pd.read_csv("datasets/mnist/mnist_train_compact.csv")
data2 = pd.read_csv("datasets/mnist/mnist_test_compact.csv")

data['index'] = data.index
data2['index'] = data2.index + len(data.index)

data.to_csv('tests/artifacts/iterators/mnist_train_compact.csv')
data2.to_csv('tests/artifacts/iterators/mnist_test_compact.csv')