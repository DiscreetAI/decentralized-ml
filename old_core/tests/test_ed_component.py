import pytest
import pandas as pd 
import numpy as np 
import json
from core.orchestrator import Orchestrator
from core.dataset import Dataset


@pytest.fixture(scope='session')
def fruit_df():
    df = pd.DataFrame()
    df['fruit'] = ['Apple']
    df['size'] = ['Large']
    df['color'] = ['red']
    return df

@pytest.fixture(scope='session')
def fruit_dataset(fruit_df):
    fruit_dict = {}

    key = 'dataset1'
    value = (fruit_df.to_json(), fruit_df.describe().to_json())
    data_tuple = (key, value)

    return Dataset(data_tuple)

@pytest.fixture
def orchestrator(fruit_dataset):
    orchestrator = Orchestrator(None, None, None, None)
    orchestrator.datasets = [fruit_dataset] * 5
    return orchestrator

def test_validate_dataset(orchestrator):
    """
    Tests validation by the Orchestrator on datasets indices access. 
         1. Tests success when accessing a valid index.
        2. Tests failure when accessing an invalid index.
        3. Tests that we cannot access a dataset when no datasets available.
    """
    orchestrator._validate_dataset(3)
    with pytest.raises(AssertionError, match='Index must be non-negative.', message='Expecting: AssertionError due to negative index.'):
        orchestrator._validate_dataset(-4)
    with pytest.raises(AssertionError, match='Index out of range. Length of datasets is {0}'.format(len(orchestrator.datasets), message='Expecting: AssertionError due to index out of bounds.')):
        orchestrator._validate_dataset(20)
    orchestrator.datasets = list()
    with pytest.raises(AssertionError, match='No datasets available, make sure to query to create datasets.', message='Expecting: AssertionError due to empty datasets.'):
        orchestrator._validate_dataset(1)

def test_validate_column(orchestrator): 
    """
    Tests validation by the Orchestrator on dataframes' columns properties. 
        1. Tests success when accessing a valid column.
        2. Tests failure when accessing an invalid column.
        3. Tests failure when accessing a column in a dataframe but with non-numerical values.
    """
    df1 = pd.DataFrame(np.random.randn(50, 4), columns=list('ABCD'))
    orchestrator._validate_column(df1, 'A')
    s = '[{"Country":"USA","Name":"Ryan"},{"Country":"Sweden","Name":"Sam"},{"Country":"Brazil","Name":"Ralf"}]'
    df2 = pd.DataFrame(json.loads(s))
    with pytest.raises(AssertionError, match= 'Invalid column E', message='Expecting: AssertionError due to non-existent column.'):
        orchestrator._validate_column(df1, 'E')
    with pytest.raises(AssertionError, match='Column type must be numerical, not {0}.'.format(df2['Country'].dtype), message='Expecting: AssertionError due to non-numerical type.'):
        orchestrator._validate_column(df2, 'Country')
