import pytest
import pandas as pd 
import numpy as np 
import json
from core import *


def test_validate_ed_dataset():
    """
    Tests validation by the Orchestrator on ed_datasets indices access. 
    """
    orchestrator = Orchestrator()
    orchestrator.ed_datasets = [{'dataset0_fruit': ('fruit', {'fruit': 'Apple', 'size': 'Large', 'color': 'Red'})},
         {'dataset1_fruit': ('fruit', {'fruit': 'Orange', 'size': 'Medium', 'color': 'Purple'})}, 
         {'dataset2_fruit': ('fruit', {'fruit': 'Berries', 'size': 'Mini', 'color': 'Orange'})}, 
         {'dataset3_fruit': ('fruit', {'fruit': 'Grapes', 'size': 'XL', 'color': 'Yellow'})}, 
         {'dataset4_fruit': ('fruit', {'fruit': 'Candy', 'size': 'Small', 'color': 'Red'})}, 
         {'dataset5_fruit': ('fruit', {'fruit': 'Chocolate', 'size': 'Large', 'color': 'Blue'})},
         {'dataset6_fruit': ('fruit', {'fruit': 'Bla', 'size': 'Small', 'color': 'Green'})}, 
         {'dataset0_games': ('games', {'real': 10, 'barca': 0})},
         {'dataset1_games': ('games', {'real': 2, 'barca': 4})},
         {'dataset2_games': ('games', {'real': 0, 'barca': 20})},
         {'dataset3_games': ('games', {'real': 1, 'barca': 3})},
         {'dataset4_games': ('games', {'real': 0, 'barca': 4})},
         {'dataset5_games': ('games', {'real': 9, 'barca': 7})},
         {'dataset6_games': ('games', {'real': 1, 'barca': 6})}]
    orchestrator.validate_ed_dataset(3)
    with pytest.raises(AssertionError):
        orchestrator.validate_ed_dataset(-4)
    with pytest.raises(AssertionError):
        orchestrator.validate_ed_dataset(20)

def test_validate_column(): 
    """
    Tests validation by the Orchestrator on dataframes' columns properties. 
    """
    orchestrator = Orchestrator()
    df1 = pd.DataFrame(np.random.randn(50, 4), columns=list('ABCD'))
    s = '[{"Country":"USA","Name":"Ryan"},{"Country":"Sweden","Name":"Sam"},{"Country":"Brazil","Name":"Ralf"}]'
    df2 = pd.DataFrame(json.loads(s))
    orchestrator.validate_column(df1, 'A')
    with pytest.raises(AssertionError):
        orchestrator.validate_column(df2, 'Country')
    with pytest.raises(AssertionError):
        orchestrator.validate_column(df1, 'E')
