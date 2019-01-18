class DMLRequest(object):
    """
    DMLRequest

    - Stores participants and other details about training for modularity.
    - Similar to the DMLObject/DMLResult in the UNIX Service.
    """
    def __init__(self):
        """
        Initialize attributes to None, set them later on.
        """
        self.model = None
        self.participants = []
        self.batch_size = None
        self.epochs = None
        self.split = None
        self.avg_type = None
        self.opt_type = None
        self.num_rounds = None