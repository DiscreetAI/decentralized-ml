from keras.models import Sequential
from keras.layers import Dense

from generic_model import GenericKerasModel
# from models.generic_model import GenericKerasModel

class KerasPerceptron(GenericKerasModel):
    def __init__(self, is_training=False):
        self.n_input = 784
        self.n_hidden1 = 200
        self.n_hidden2 = 200
        self.n_classes = 10
        self.is_training = is_training
        self.model = self.build_model()
        if is_training:
            self.compile_model()

    def build_model(self):
        model = Sequential()
        model.add(Dense(self.n_hidden1, input_dim=self.n_input, activation='relu'))
        model.add(Dense(self.n_hidden2, activation='relu'))
        model.add(Dense(self.n_classes, activation='linear'))
        model.summary()
        return model

    def compile_model(self):
        self.model.compile(
            optimizer='sgd',
            loss='categorical_crossentropy',
            metrics=['acc']
        )

if __name__ == '__main__':
    m = KerasPerceptron(is_training=True)

    # m.build_optimizer(1.47)
    # m.train(text, {"epochs":1, "batch_size":8})
