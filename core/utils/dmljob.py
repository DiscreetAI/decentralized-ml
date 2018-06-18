import numpy as np

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
    weights = np.array(dmljob_obj.weights).tostring()
    rest = {
        'job_type': dmljob_obj.job_type,
        'serialized_model': dmljob_obj.serialized_model,
        'model_type': dmljob_obj.model_type,
        'config': dmljob_obj.config,
        'hyperparams': dmljob_obj.hyperparams,
        # 'labeler': dmljob_obj.labeler # Removed because it's a function!
    }
    return {
        'weights': weights,
        'job_data': rest
    }

def deserialize_job(serialized_job):
    weights = np.fromstring(serialized_job['weights'])
    rest = serialized_job['job_data']
    return DMLJob(
        rest['job_type'],
        rest['serialized_model'],
        rest['model_type'],
        rest['config'],
        weights,
        rest['hyperparams'],
        # rest['labeler'] # Removed because it's a function!
    )
