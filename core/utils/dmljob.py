class DMLJob(object):
    """
    DML Job

    """

    def __init__(self, serialized_model, job_type='initialize', model_type='keras', config={},
        weights=None, hyperparams=None, labeler=None):
        self.job_type = job_type
        self.serialized_model = serialized_model
        self.model_type = model_type
        self.config = config
        self.weights = weights
        self.hyperparams = hyperparams
        self.labeler = labeler
