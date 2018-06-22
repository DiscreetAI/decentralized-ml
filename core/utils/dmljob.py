import numpy as np

from core.utils.keras import serialize_weights, deserialize_weights

class DMLJob(object):
    """
    DML Job

    """

    def __init__(
        self,
        job_type,
        serialized_model,
        model_type,
        config={},
        weights=None,
        hyperparams=None,
        labeler=None
        ):
        self.job_type = job_type
        self.serialized_model = serialized_model
        self.model_type = model_type
        self.config = config
        self.weights = weights
        self.hyperparams = hyperparams
        self.labeler = labeler


def serialize_job(dmljob_obj):
    rest = {
        'job_type': dmljob_obj.job_type,
        'serialized_model': dmljob_obj.serialized_model,
        'model_type': dmljob_obj.model_type,
        'config': dmljob_obj.config,
        'hyperparams': dmljob_obj.hyperparams,
        # 'labeler': dmljob_obj.labeler # Removed because it's a function!
    }
    return {
        'weights': serialize_weights(dmljob_obj.weights),
        'job_data': rest
    }

def deserialize_job(serialized_job):
    rest = serialized_job['job_data']
    return DMLJob(
        rest['job_type'],
        rest['serialized_model'],
        rest['model_type'],
        rest['config'],
        desirialize_weights(serialized_job['weights']),
        rest['hyperparams'],
        # rest['labeler'] # Removed because it's a function!
    )
