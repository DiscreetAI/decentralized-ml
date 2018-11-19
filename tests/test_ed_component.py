import pytest
import pandas as pd 
import numpy as np 
import json
from core import *

@pytest.fixture
def orchestrator():
    return Orchestrator();


def test_validate_ed_dataset(orchestrator):
    """
    Tests validation by the Orchestrator on ed_datasets indices access. 
         1. Tests success when accessing a valid index.
        2. Tests failure when accessing an invalid index.
        3. Tests that we cannot access a dataset when no datasets available.
    """
    ed_datasets = [{'dataset0_fruit': ('fruit', {'fruit': 'Apple', 'size': 'Large', 'color': 'Red'})},
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
    orchestrator.ed_datasets = ed_datasets
    orchestrator.validate_ed_dataset(3)
    with pytest.raises(AssertionError, match='Index must be non-negative.', message='Expecting: AssertionError'):
        orchestrator.validate_ed_dataset(-4)
    with pytest.raises(AssertionError, match='Index out of range. Length of datasets is {0}'.format(len(ed_datasets), message='Expecting: AssertionError')):
        orchestrator.validate_ed_dataset(20)
    orchestrator.ed_datasets = list()
    with pytest.raises(AssertionError, match='No datasets available, make sure to query to create datasets.', message='Expecting: AssertionError'):
        orchestrator.validate_ed_dataset(1)

def test_validate_column(orchestrator): 
    """
    Tests validation by the Orchestrator on dataframes' columns properties. 
        1. Tests success when accessing a valid column.
        2. Tests failure when accessing an invalid column.
        3. Tests failure when accessing a column in a dataframe but with non-numerical values.
    """
    df1 = pd.DataFrame(np.random.randn(50, 4), columns=list('ABCD'))
    orchestrator.validate_column(df1, 'A')
    s = '[{"Country":"USA","Name":"Ryan"},{"Country":"Sweden","Name":"Sam"},{"Country":"Brazil","Name":"Ralf"}]'
    df2 = pd.DataFrame(json.loads(s))
    with pytest.raises(AssertionError, match= 'Invalid column E', message='Expecting: AssertionError'):
        orchestrator.validate_column(df1, 'E')
    with pytest.raises(AssertionError, match='Column type must be numerical, not {0}.'.format(df2['Country'].dtype), message='Expecting: AssertionError'):
        orchestrator.validate_column(df2, 'Country')
