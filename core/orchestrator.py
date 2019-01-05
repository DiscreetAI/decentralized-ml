from ipywidgets import widgets
from IPython.display import display, Image
from core.category_component import CategoryComponent
from core.db_client import DBClient
import pandas as pd
from core.ed_component import EDComponent
import numpy as np


OPTIONS = ['histogram', 'scatter', 'compare using scatter', 'describe','compare using describe']

class Orchestrator(object):
    """
    Orchestrator Class
    
    - Manages logic between DBClient, EDComponent, and CategoryComponent. 
    - Gets input from user with the help of DLDL Notebook.
    """ 
    def __init__(self, category_component, ed_component):
        """
        Initialize Orchestrator instance.
        """
        self.category_component = category_component
        self.ed_component = ed_component
        self.datasets = list()
        self.method = None
        self.dataset1_index = None
        self.dataset2_index = None
        self.column1 = None
        self.column2 = None
 
    def get_dataset_samples(self):
        """
        Return a list of dataset samples to the user.
        """
        return [dataset.sample for dataset in self.datasets]

    def category_name(self):
        """
        Displays:
            Prompt to get category from user.
        """
        def orchestrate(sender):
            """
            This method is triggered by the button.on_click event
            It uses the current value of category_widget variable
            to get the dictionary with ed and stores the value in
            a global var.
            """
            sender.disabled = True
            category_text = category_widget.value.strip().lower()
            result = self.category_component.get_datasets_with_category(category_text)
            if result['Success']:
                self.datasets = result['Result']
            else:
                print(result['Error'])
            sender.disabled = False


        category_widget = widgets.Text(
            value=None,
            placeholder='',
            description='Category:',
            disabled=False,

        )
        button = widgets.Button(description='Submit')
        display(category_widget)
        display(button)
        button.on_click(orchestrate)

    def visualization_parameters(self):
            """
            Displays:
                Prompt to get visualization information from user. 
                (Only for directories)
            """
            def store(sender):
                """
                
                """
                sender.disabled = True
                self.method = method_widget.value.strip()
                self.dataset1_index = dataset1_widget.value.strip()
                self.dataset2_index = dataset2_widget.value.strip()
                self.column1 = column1_widget.value.strip()
                self.column2 = column2_widget.value.strip()
                sender.disabled = False

            dataset1_widget = widgets.Text(
                value=None,
                placeholder='',
                description='Dataset 1:',
                disabled=False,

            )
            dataset2_widget = widgets.Text(
                value=None,
                placeholder='',
                description='Dataset 2:',
                disabled=False,

            )
            column1_widget = widgets.Text(
                value=None,
                placeholder='',
                description='Column 1:',
                disabled=False,

            )
            column2_widget = widgets.Text(
                value=None,
                placeholder='',
                description='Column 2:',
                disabled=False,

            )
            method_widget = widgets.RadioButtons(
                options=OPTIONS,
                value='histogram',
                description='Method:',
                disabled=False
            )
            button = widgets.Button(description='Submit')

            display(method_widget)
            display(dataset1_widget)
            display(dataset2_widget)
            display(column1_widget)
            display(column2_widget)
            display(button)
            button.on_click(store)

    def visualize(self): 
        """
        Returns the corresponding plot.
        There are five different options to call methods in self.ed_component on.
        OPTIONS[0]: 'histogram' needs one dataset json and one column.
        OPTIONS[1]: 'scatter' needs one dataset json and two columns.
        OPTIONS[2]: 'compare using scatter' needs two datasets json and two columns.
        OPTIONS[3}: 'describe' needs one dataset and one column.
        OPTIONS[4]: 'compare using describe' needs two datasets and two corresponding columns.
        """
        if (self.method == OPTIONS[0]):
            self.dataset1_index = int(self.dataset1_index)
            self.validate_dataset(self.dataset1_index)
            dataset1 = self.datasets[self.dataset1_index]
            df = dataset1.sample

            self.validate_column(df, self.column1)
            return self.ed_component.histogram(df, self.column1)

        elif (self.method == OPTIONS[1]):
            self.dataset1_index = int(self.dataset1_index)
            self.validate_dataset(self.dataset1_index)

            dataset1 = self.datasets[self.dataset1_index]
            df = dataset1.sample
            self.validate_column(df, self.column1)
            self.validate_column(df, self.column2)

            return self.ed_component.scatter(df, self.column1, self.column2)

        elif (self.method == OPTIONS[2]):
            self.dataset1_index = int(self.dataset1_index)
            self.dataset1_index = int(self.dataset1_index)
            self.dataset2_index = int(self.dataset2_index)
            self.validate_dataset(self.dataset1_index)
            self.validate_dataset(self.dataset2_index)

            dataset1 = self.datasets[self.dataset1_index]
            df1 = dataset1.sample
            self.validate_column(df1, self.column1)

            dataset2 = self.datasets[self.dataset2_index]
            df2 = dataset2.sample
            self.validate_column(df2, self.column1)

            return self.ed_component.scatter_compare(df1, df2, self.column1, self.column2)

        elif (self.method == OPTIONS[3]):
            self.dataset1_index = int(self.dataset1_index)
            self.validate_dataset(self.dataset1_index)

            dataset1 = self.datasets[self.dataset1_index]
            df = dataset1.metadata
            self.validate_column(df, self.column1)
            metadata1 = df[self.column1]

            return metadata1

        elif (self.method == OPTIONS[4]):
            self.dataset1_index = int(self.dataset1_index)
            self.dataset2_index = int(self.dataset2_index)
            self.validate_dataset(self.dataset1_index)
            self.validate_dataset(self.dataset2_index)

            dataset1 = self.datasets[self.dataset1_index]
            df = dataset1.metadata
            self.validate_column(df, self.column1)
            metadata1 = df[self.column1]

            dataset2 = self.datasets[self.dataset2_index]
            df2 = dataset2.metadata
            self.validate_column(df2, self.column2)
            metadata2 = df2[self.column2]

            return metadata1, metadata2

        else: 
            error_message = 'Could not plot, invalid input format.'
            raise Exception(error_message)

    def validate_dataset(self, dataset_index):
        assert len(self.datasets) != 0, 'No datasets available, make sure to query to create datasets.'
        assert dataset_index >= 0, 'Index must be non-negative.' 
        assert len(self.datasets) > dataset_index, 'Index out of range. Length of datasets is {0}.'.format(len(self.datasets)) 


    def validate_column(self, df, column):
        assert column in df.columns, 'Invalid column {0}'.format(column)
        assert np.issubdtype(df[column].dtype, np.number), 'Column type must be numerical, not {0}.'.format(df[column].dtype) 
