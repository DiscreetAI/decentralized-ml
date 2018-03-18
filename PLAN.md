## Things to do

1. Set up client-server architecture
  1. Experiment class that creates K clients on different threads and 1 server
  1. Clients will be listening, waiting for the server to send a job (train job)
  1. Once a client receive the job, it performs computations (SGD) and sends back a result (weight updates) the server
  1. As the server receives the results (weight updates), it does more work (stores the weight so it can then perform averaging on the main model)
  1. Experiment will specify the number of clients K, the model type m, the dataset d, the local minibatch size B, the number of local epochs E, the learning rate n, and the fraction of active clients C.


1. Implement Federated Averaging
  1. The type of model will be defined by the `-m`/`--model` parameter in Experiment
  1. The server and each client will all have a copy of the model architecture
  1. The server will initialize the model weights (randomly)
  1. The server will randomly choose C * K clients to train on
  1. On each round...
    1. The server will send the current weights to each client as well as a training job
    1. The clients will train on their own thread using the hyperparameters B, E, and n. Once finished, they will send the updates back to the server
    1. Once the server has all the updates, it will average the weights and update the main model
    1. The server will then validate accuracy on a held-out test set
    1. Finally, the server will perform another round


1. Implement a GenericModel class
  1. Needs to support the following:
    1. Set up the computation graph of a specified deep model (`build()`)
    1. Load the weights from a pre-specified state (`load_weights()`)
      1. This will be sent by the server
    1. Retrieve minibatches of size B from a local dataset d (`get_next_batch()`)
    1. Train the graph on the B-minibatches for E epochs and learning rate n (`train()`)
    1. Return the learned weights (`get_weights()`)


1. Implement the 4 models, extending the GenericModel class
  1. Multi-layer perceptron model
  1. 2-layer CNN model
  1. CIFAR CNN model
  1. 2-layer character LSTM
  1. Test that these models work by training them on their respective datasets and standard SGD


1. Run experiments
  1. _To be defined_
