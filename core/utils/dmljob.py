from copy import deepcopy
import numpy as np

from core.utils.keras import serialize_weights, deserialize_weights
from core.utils.enums import JobTypes

class DMLJob(object):
    """
    DML Job

    This class represents a generic job that the Scheduler and Runners can
    execute.

    """

    def __init__(
        self,
        job_type,
        serialized_model,
        framework_type,
        weights=None,
        hyperparams=None,
        label_column_name=None,
        uuid=None,
        raw_filepath=None,
        session_filepath=None,
        datapoint_count=None
        ):
        """
        Initializes a DML Job object.

        Args:
            job_type (str): the job type.
            serialized_model (dict): the model to train in a serialized format.
            framework_type (str): the type of framework the model is in [keras].
            weights (list): list of np.arrays representing the weights of a model.
            hyperparams (dict): hyperparameters for training/validating a model.
            label_column_name (str): string that represents which column of the
                                     transformed dataset contains the labels for
                                     supervised training.
            raw_filepath (str): the filepath to the folder that contains the
                                raw data before transform and training-test  
                                split. Only one dataset file supported per
                                folder at the moment.
            session_filepath (str): the filepath to the folder that contains
                                    the raw data after applying the transform
                                    function and training-test split. Assumes
                                    `train.csv` and `test.csv` are in folder.
            datapoint_count (int): Number of datapoints after applying
                                   transform function.
            new_weights (list): list of np.arrays representing the weights that
                                should be averaged with 'weights'
            omega (float): the weight given to new_weights in weighted averaging
            sigma_omega (float): the sum of omega's incorporated into weighted
                                averaging so far. Kept in the DMLJob to allow the
                                weighted average to be unrolled.
        """
        self.job_type = job_type
        self.serialized_model = serialized_model
        self.framework_type = framework_type
        self.weights = weights
        self.hyperparams = hyperparams
        self.label_column_name = label_column_name
        self.omega = None
        self.sigma_omega = None
        self.new_weights = None
        self.uuid = uuid
        self.raw_filepath = raw_filepath
        self.session_filepath = session_filepath
        self.datapoint_count = datapoint_count
    
    def copy_constructor(self):
        newjob = deepcopy(self)
        return newjob

def serialize_job(dmljob_obj):
    """
    Serializes a DML Job object into a dictionary.

    Args:
        dmljob_obj (DMLJob): job object.

    Returns:
        dict: The serialized version of the DML Job.
    """
    assert isinstance(dmljob_obj, DMLJob), "Cannot serialize_job a non-DMLJob!"
    rest = {
        'job_type': dmljob_obj.job_type,
        'serialized_model': dmljob_obj.serialized_model,
        'framework_type': dmljob_obj.framework_type,
        'hyperparams': dmljob_obj.hyperparams,
        'label_column_name': dmljob_obj.label_column_name,
        'uuid': dmljob_obj.uuid,
        'raw_filepath': dmljob_obj.raw_filepath,
        'session_filepath': dmljob_obj.session_filepath,
        'datapoint_count': dmljob_obj.datapoint_count,
        'omega': dmljob_obj.omega,
        'sigma_omega': dmljob_obj.sigma_omega,
    }
    weights = None
    if dmljob_obj.weights:
        weights = serialize_weights(dmljob_obj.weights)
    return {
        'weights': weights,
        'job_data': rest,
    }

def deserialize_job(serialized_job):
    """
    Deserializes a serialized version of a DML Job object.

    Args:
        serialized_job (dict): serialized version of a DML Job object.

    Returns:
        DMLJob: A DML Job object from serialized_job.
    """
    rest = serialized_job['job_data']
    weights = None
    if serialized_job.get('weights', None):
        weights = deserialize_weights(serialized_job['weights'])
    job = DMLJob(
        rest['job_type'],
        rest['serialized_model'],
        rest['framework_type'],
        weights,
        rest['hyperparams'],
        rest['label_column_name'],
        rest['uuid'],
        rest['raw_filepath'],
        rest['session_filepath'],
        rest['datapoint_count']
    )
    job.omega = rest['omega']
    job.sigma_omega = rest['sigma_omega']
    return job
