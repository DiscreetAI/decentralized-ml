import context

from custom.keras               import get_optimizer
from core.runner                import DMLRunner
from models.keras_perceptron    import KerasPerceptron
from core.utils.dmljob          import DMLJob, serialize_job, deserialize_job
from examples.labelers          import mnist_labeler


def get_dataset_path():
    return 'datasets/mnist'


def get_config():
    return {}


def get_model_json():
    m = KerasPerceptron(is_training=True)
    model_architecture = m.model.to_json()
    model_optimizer = get_optimizer(m.model)
    model_json = {
        "architecture": model_architecture,
        "optimizer": model_optimizer
    }
    return model_json


def get_initialize_job(model_json):
    initialize_job = DMLJob(
        "initialize",
        model_json,
        "keras"
    )
    return initialize_job


def get_hyperparams():
    hyperparams = {
        'averaging_type': 'data_size',
        'batch_size': 50,
        'epochs': 1,
        'split': 0.8,
    }
    return hyperparams


def get_train_job(model_json, initial_weights):
    train_job = DMLJob(
        "train",
        model_json,
        "keras",
        config,
        initial_weights,
        hyperparams,
        mnist_labeler
    )
    return train_job


def get_validate_job(model_json, new_weights):
    validate_job = DMLJob(
        "validate",
        model_json,
        'keras',
        config,
        new_weights,
        hyperparams,
        mnist_labeler
    )
    return validate_job


config = get_config()
hyperparams = get_hyperparams()
model_json = get_model_json()

runner = DMLRunner(get_dataset_path(), config)

initialize_job = get_initialize_job(model_json)
initial_weights = runner.run_job(initialize_job)

train_job = get_train_job(model_json, initial_weights)
new_weights, omega, train_stats = runner.run_job(train_job)

validate_job = get_validate_job(model_json, new_weights)
val_stats = runner.run_job(validate_job)
