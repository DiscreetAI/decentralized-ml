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
    def __init__(self, category_component, ed_component, dml_client):
        """
        Initialize Orchestrator instance.
        """
        self.category_component = category_component
        self.ed_component = ed_component
        self.dml_client = dml_client
        self.datasets = list()
        self.uuid_to_dataset = dict()
        self.method = None
        self.dataset1_index = None
        self.dataset2_index = None
        self.column1 = None
        self.column2 = None
        self.default_style = {'description_width': 'initial'}
        self.participants = []
        self.batch_size = None
        self.epochs = None
        self.split = None
        self.avg_type = None
        self.opt_type = None
        self.num_rounds = None
 
    def get_datasets(self):
        """
        Return a list of dataset samples to the user.
        """
        return self.datasets

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
                self.datasets = result['datasets']
                self.uuid_to_dataset = result['uuid_to_dataset']
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
                description='Dataset 1',
                disabled=False,

            )
            dataset2_widget = widgets.Text(
                value=None,
                placeholder='',
                description='Dataset 2',
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

    def select_datasets(self):
        """
        Display frontend for selecting datasets.
        """
        add_tab_button = widgets.Button(description='Add Dataset')
        remove_tab_button = widgets.Button(description='Remove Dataset')

        def add_tab(sender):
            children = list(tab.children)
            children.append(text_list)
            tab.children = children
            tab.set_title(len(children) - 1, 'Dataset {}'.format(len(children)))

        def remove_tab(sender):
            children = list(tab.children)
            if len(children) > 1:
                children.pop()
            tab.children = children

        add_tab_button.on_click(add_tab)
        remove_tab_button.on_click(remove_tab)
        button_list = widgets.HBox([add_tab_button, remove_tab_button])

        uuid_text = widgets.Text(description='UUID')
        label_column_text = widgets.Text(
                description='Label Column Name', 
                style=self.default_style
            )
        text_arr = [uuid_text, label_column_text, button_list]
        text_list = widgets.VBox(text_arr)
        text_list.texts = text_arr

        tab = widgets.Tab()
        tab.children = []
        add_tab(None)

        display(tab)

        def set_up_participants(sender):
            sender.disabled = True

            participants = []
            for dataset in tab.children:
                uuid_widget, label_column_widget = dataset.texts
                uuid = uuid_text.value.strip()
                label_column_name = label_column_widget.value.strip()
                self._validate_participant(uuid, label_column_name)
                participants.append(
                    {
                        'dataset_uuid': uuid,
                        'label_column_name': label_column_name
                    }
                )
            self.participants = participants

            sender.disabled = False

        button = widgets.Button(description='Submit')
        display(button)

    def parameters(self):
        """
        Display frontend for entering in rest of DML parameters.
        """
        def store(sender):
            """
            Validate parameters, and then store them.
            """
            sender.disabled = True

            batch_size = batch_widget.value.strip()
            epochs = epochs_widget.value.strip()
            split = split_widget.value.strip()
            avg_type = avg_type_widget.value.strip()
            opt_type = opt_type_widget.value.strip()
            num_rounds = num_rounds_widget.value.strip()

            self._validate_parameters(batch_size, epochs, split, avg_type, \
                opt_type, num_rounds)

            self.batch_size = int(batch_size)
            self.epochs = int(epochs)
            self.split = float(split)
            self.avg_type = avg_type
            self.opt_type = opt_type
            self.num_rounds = int(num_rounds)

            sender.disabled = False

        batch_widget = widgets.Text(
            value=None,
            placeholder='',
            description='Batch Size:',
            disabled=False,

        )
        epochs_widget = widgets.Text(
            value=None,
            placeholder='',
            description='Epochs:',
            disabled=False,
        )
        split_widget = widgets.Text(
            value=None,
            placeholder='',
            description='Split:',
            disabled=False,

        )
        avg_type_widget = widgets.Text(
            value=None,
            placeholder='',
            description='Avg Type:',
            disabled=False,

        )
        opt_type_widget = widgets.Text(
            options=OPTIONS,
            placeholder='',
            description='Opt Type:',
            disabled=False
        )
        num_rounds_widget = widgets.Text(
            options=OPTIONS,
            placeholder='',
            description='# of Rounds:',
            disabled=False
        )
        button = widgets.Button(description='Submit')

        display(batch_widget)
        display(epochs_widget)
        display(split_widget)
        display(avg_type_widget)
        display(opt_type_widget)
        display(num_rounds_widget)

        button.on_click(store)
        display(button)

    def conduct_dml(self, model):
        """
        Send DML Client the necessary parameters for training of the model.
        """
        self.model = model
        self._sanity_check_dml_request()
        self.dml_client.decentralized_learn(
            model=self.model,
            participants=self.participants,
            batch_size=self.batch_size,
            epochs=self.epochs,
            split=self.split,
            avg_type=self.avg_type,
            opt_type=self.opt_type,
            num_rounds=self.num_rounds
        )

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
            self._validate_dataset(self.dataset1_index)
            dataset1 = self.datasets[self.dataset1_index]
            df = dataset1.sample

            self._validate_column(df, self.column1)
            return self.ed_component.histogram(df, self.column1)

        elif (self.method == OPTIONS[1]):
            self.dataset1_index = int(self.dataset1_index)
            self._validate_dataset(self.dataset1_index)

            dataset1 = self.datasets[self.dataset1_index]
            df = dataset1.sample
            self._validate_column(df, self.column1)
            self._validate_column(df, self.column2)

            return self.ed_component.scatter(df, self.column1, self.column2)

        elif (self.method == OPTIONS[2]):
            self.dataset1_index = int(self.dataset1_index)
            self.dataset1_index = int(self.dataset1_index)
            self.dataset2_index = int(self.dataset2_index)
            self._validate_dataset(self.dataset1_index)
            self._validate_dataset(self.dataset2_index)

            dataset1 = self.datasets[self.dataset1_index]
            df1 = dataset1.sample
            self._validate_column(df1, self.column1)

            dataset2 = self.datasets[self.dataset2_index]
            df2 = dataset2.sample
            self._validate_column(df2, self.column1)

            return self.ed_component.scatter_compare(df1, df2, self.column1, self.column2)

        elif (self.method == OPTIONS[3]):
            self.dataset1_index = int(self.dataset1_index)
            self._validate_dataset(self.dataset1_index)

            dataset1 = self.datasets[self.dataset1_index]
            df = dataset1.metadata
            self._validate_column(df, self.column1)
            metadata1 = df[self.column1]

            return metadata1

        elif (self.method == OPTIONS[4]):
            self.dataset1_index = int(self.dataset1_index)
            self.dataset2_index = int(self.dataset2_index)
            self._validate_dataset(self.dataset1_index)
            self._validate_dataset(self.dataset2_index)

            dataset1 = self.datasets[self.dataset1_index]
            df = dataset1.metadata
            self._validate_column(df, self.column1)
            metadata1 = df[self.column1]

            dataset2 = self.datasets[self.dataset2_index]
            df2 = dataset2.metadata
            self._validate_column(df2, self.column2)
            metadata2 = df2[self.column2]

            return metadata1, metadata2

        else: 
            error_message = 'Could not plot, invalid input format.'
            raise Exception(error_message)

    def _validate_dataset(self, dataset_index):
        assert len(self.datasets) != 0, 'No datasets available, make sure to query to create datasets.'
        assert dataset_index >= 0, 'Index must be non-negative.' 
        assert len(self.datasets) > dataset_index, 'Index out of range. Length of datasets is {0}.'.format(len(self.datasets)) 


    def _validate_column(self, df, column):
        assert column in df.columns, 'Invalid column {0}'.format(column)
        assert np.issubdtype(df[column].dtype, np.number), 'Column type must be numerical, not {0}.'.format(df[column].dtype) 
    
    def _validate_participant(self, uuid, label_column_name):
        """
        Validate participant information.
        """
        assert uuid in uuid_to_dataset, \
            "Dataset with UUID {} does not exist in list!".format(uuid)
        dataset = self.uuid_to_dataset[uuid]
        self._validate_column(label_column_name, dataset.sample)

    def _validate_parameters(self, batch_size, epochs, split, avg_type, \
        opt_type, num_rounds):
        """
        Validate remaining details of training in DMLRequest
        """
        assert self._is_integer(batch_size), "Batch size must be an integer!"
        assert self._is_integer(epochs), "Epochs must be an integer!"
        assert self._is_float(split), "Split must be a float!"
        assert float(split) >= 0 and float(split) <= 1, \
                "split must be between 0 and 1!"
        assert self._is_integer(num_rounds), "# of rounds must be integer!"

    def _sanity_check_dml_request(self):
        """
        Sanity check that all parameters of request are set before sending to
        DMLClient
        """
        assert self.participants, "Participants not set!"
        assert self.batch_size and self.epochs and self.dml_request.split \
            and self.avg_type and self.opt_type and self.num_rounds, \
            "Remaining parameters not set!"
        assert self.model, "Model not set!"

    def _is_float(self, string):
        """
        Helper method to determine if string is float.
        """
        try:
            float(value)
            return True
        except ValueError:
            return False

    def _is_integer(self, string):
        """
        Helper method to determine if string is integer.
        """
        return string.isdigit()

    
