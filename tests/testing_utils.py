from models.keras_perceptron    import KerasPerceptron
from custom.keras               import get_optimizer
from core.utils.enums           import JobTypes, RawEventTypes
from core.utils.dmljob          import DMLJob, serialize_job
from data.iterators             import count_datapoints

def make_dataset_path():
    return 'datasets/mnist'

def make_communicate_job(key, weights):
    communicate_job = DMLJob(
        JobTypes.JOB_COMM.name,
        key,
        "keras"
    )
    communicate_job.key = key
    return communicate_job

def make_model_json():
    m = KerasPerceptron(is_training=True)
    model_architecture = m.model.to_json()
    model_optimizer = get_optimizer(m.model)
    model_json = {
        "architecture": model_architecture,
        "optimizer": model_optimizer
    }
    return model_json

def make_initialize_job(model_json, raw_filepath=None, uuid=None):
    initialize_job = DMLJob(
        JobTypes.JOB_INIT.name,
        model_json,
        "keras",
        hyperparams=make_hyperparams(),
        label_column_name='label',
        raw_filepath=raw_filepath,
        uuid=uuid
    )
    return initialize_job

def make_split_job( \
    model_json, raw_filepath):
    split_job = DMLJob(
        JobTypes.JOB_SPLIT.name,
        model_json,
        "keras",
        hyperparams=make_hyperparams(),
        label_column_name='label',
        raw_filepath=raw_filepath,
    )
    return split_job

def make_hyperparams(split=0.004):
    hyperparams = {
        'averaging_type': 'data_size',
        'batch_size': 4,
        'epochs': 1,
        'split': 1,
    }
    return hyperparams

def make_train_job(model_json, initial_weights, hyperparams, \
    session_filepath, datapoint_count):
    train_job = DMLJob(
        JobTypes.JOB_TRAIN.name,
        model_json,
        "keras",
        initial_weights,
        hyperparams,
        'label',
        session_filepath = session_filepath,
        datapoint_count = datapoint_count
    )
    return train_job

def make_serialized_job(raw_filepath):
    initialize_job = make_initialize_job(
                        make_model_json(), 
                        raw_filepath=raw_filepath
                    )
    serialized_job = serialize_job(initialize_job)
    return serialized_job

def make_serialized_job_with_uuid(uuid):
    initialize_job = make_initialize_job(make_model_json(), uuid=uuid)
    serialized_job = serialize_job(initialize_job)
    return serialized_job

def make_validate_job(model_json, new_weights, hyperparams, \
    session_filepath, datapoint_count):
    validate_job = DMLJob(
        JobTypes.JOB_VAL.name,
        model_json,
        'keras',
        new_weights,
        hyperparams,
        'label',
        session_filepath = session_filepath,
        datapoint_count = datapoint_count
    )
    return validate_job