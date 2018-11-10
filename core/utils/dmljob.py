import numpy as np

from core.utils.keras import serialize_weights, deserialize_weights

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
        label_column_name=None
        ):
        """
        Initializes a DML Job object.

        Args:
            job_type (str): the job type.
            serialized_model (dict): the model to train in a serialized format.
            framework_type (str): the type of framework the model is in [keras].
            weights (list): list of np.arrays representing the weghts of a model.
            hyperparams (dict): hyperparameters for training/validating a model.
            label_column_name (str): string that represents which column of the
                                     transformed dataset contains the labels for
                                     supervised training.

        """
        self.job_type = job_type
        self.serialized_model = serialized_model
        self.framework_type = framework_type
        self.weights = weights
        self.hyperparams = hyperparams
        self.label_column_name = label_column_name


    def set_weights(self, current_weights, new_weights, omega, sigma_omega):
        """
        NOTE: This function is used to get relevant information into the DMLJob
        for averaging. It will be deprecated in future.
        """
        self.weights = current_weights
        self.new_weights = new_weights
        self.omega = omega
        self.sigma_omega = sigma_omega

def serialize_job(dmljob_obj):
    """
    Serializes a DML Job object into a dictionary.

    Args:
        dmljob_obj (DMLJob): job object.

    Returns:
        dict: The serialized version of the DML Job.
    """
    rest = {
        'job_type': dmljob_obj.job_type,
        'serialized_model': dmljob_obj.serialized_model,
        'framework_type': dmljob_obj.framework_type,
        'hyperparams': dmljob_obj.hyperparams,
        'label_column_name': dmljob_obj.label_column_name,
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
    return DMLJob(
        rest['job_type'],
        rest['serialized_model'],
        rest['framework_type'],
        weights,
        rest['hyperparams'],
        rest['label_column_name'],
    )
