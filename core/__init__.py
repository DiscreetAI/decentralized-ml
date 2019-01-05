from core.orchestrator import Orchestrator
from ipywidgets import widgets
from IPython.display import display, Image
from core.category_component import CategoryComponent
from core.db_client import DBClient
import pandas as pd
from core.ed_component import EDComponent
from core.blockchain_client import BlockchainClient
import numpy as np


class Explora(Orchestrator):
    """
    Directly called by user to set up Orchestrator and components it uses.
    """
    def __init__(self):
        """
        Wrapper around Orchestrator so that:

        1. User simply has to call "explora.<command>" to execute functions
           in Orchestrator
        2. We maintain use of dependency injection, which simplifies testing.
        """
        db_client = DBClient()
        blockchain_client = BlockchainClient()
        category_component = CategoryComponent(db_client, blockchain_client)
        ed_component = EDComponent()
        Orchestrator.__init__(self, category_component, ed_component)

