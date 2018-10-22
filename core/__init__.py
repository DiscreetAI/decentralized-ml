from ipywidgets import widgets
from IPython.display import display, Image
from core.category_component import CategoryComponent
from core.db_client import DBClient
import pandas as pd
from core.ed_component import EDComponent
import numpy as np

OPTIONS = ['histogram', 'scatter', 'compare using scatter', 'compare using describe','compare using columns']

class Orchestrator(object):
	"""
	Orchestrator Class

	- 
	""" 
	def __init__(self):
		"""
		Initialize Orchestrator instance.
		"""
		self.db_client = DBClient()
		self.category_component = CategoryComponent(db_client)
		self.ed_component = EDComponent()
		self.ed_directories = []
		self.method = None
		self.directory1 = None
		self.directory2 = None
		self.dataset1 = None
		self.dataset2 = None
		self.column1 = None
		self.column2 = None
 
	def get_ed_directories(self):
		"""
		Returns ed_directories to the user,
		this is a list.
		"""
		try:
			return self.ed_directories
		except Exception as inst:
			print(inst)

	def get_ed_directory(self, directory_index):
		"""
		Returns a dictionary in ed_directories to the user.

		@param integer directory_index: index of corresponding directory
		"""
		# TODO: catch exceptions
		try:
			return self.ed_directories[directory_index]
		except Exception as inst:
			print(inst)

	def get_datasets(self, directory_index):
		"""
		Returns a list of all datasets available for corresponding 
		directory in directory_index position.

		@param integer directory_index: index of corresponding directory
		"""
		try:
			ed_directory = self.ed_directories[directory_index]
			return ed_directory.keys()
		except Exception as inst:
			print(inst)

	def get_dataset(self, directory_index, dataset_key):
		"""
		Returns a dataframe of the dataset dataset of directory in
		directory_index position

		@param integer directory_index: index of corresponding directory
		@param object dataset_key: key of the dataset in the corresponding
		directory
		"""
		# TODO: catch exceptions
		try: 
			ed_directory = self.ed_directories[directory_index]
			dataset = ed_directory.get(dataset_key)
			key = dataset.keys()[0]
			df = pd.read_json(dataset.get(key))
			return df
		except Exception as inst:
			print(inst)

	def check(self):
		return self.method, self.columns, self.json_indexes

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
			cc_dict = self.category_component.get_ed_with_category(category_text)
			# TODO: change this to the actual value of the dictionary, it should not be jsut the category text
			# global ed_directories
			self.ed_directories = None
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
				self.directory1 = directory1_widget.value.strip()
				self.directory2 = directory2_widget.value.strip()
				self.dataset1 = dataset1_widget.value.strip()
				self.dataset2 = dataset2_widget.value.strip()
				self.column1 = column1_widget.value.strip()
				self.column2 = column2_widget.value.strip()
				sender.disabled = False

			directory1_widget = widgets.Text(
				value=None,
				placeholder='',
				description='Directory 1:',
				disabled=False,

			)
			directory2_widget = widgets.Text(
				value=None,
				placeholder='',
				description='Directory 2:',
				disabled=False,

			)
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
			display(directory1_widget)
			display(directory2_widget)
			display(dataset1_widget)
			display(dataset2_widget)
			display(column1_widget)
			display(column2_widget)
			display(button)
			button.on_click(store)

	def visualize(self): 
		"""
		Returns the corresponding plot.
		"""
		try: 
			if (self.method == OPTIONS[0]):
				ed_directory = self.ed_directories[self.directory1]
				dataset = ed_directory.get(self.dataset1)
				key = dataset.keys()[0]
				df = pd.read_json(dataset.get(key))
				return self.ed_component.histogram(df, self.column1)
			elif (self.method == OPTIONS[1]):
				ed_directory = self.ed_directories[self.directory1]
				dataset = ed_directory.get(self.dataset1)
				key = dataset.keys()[0]
				df = pd.read_json(dataset.get(key))
				return self.ed_component.scatter(df, self.column1, self.column2)
			elif (self.method == OPTIONS[2]):
				ed_directory1 = self.ed_directories[self.directory1]
				dataset1 = ed_directory.get(self.dataset1)
				key1 = dataset.keys()[0]
				df1 = pd.read_json(dataset.get(key1))

				ed_directory2 = self.ed_directories[self.directory2]
				dataset2 = ed_directory.get(self.dataset2)
				key2 = dataset.keys()[0]
				df2 = pd.read_json(dataset.get(key2))
				return self.ed_component.scatter_compare(df1, df2, self.column1, self.column2)
			elif (self.method == OPTIONS[3]):
				ed_directory1 = self.ed_directories[self.directory1]
				dataset1 = ed_directory.get(self.dataset1)
				key1 = dataset.keys()[0]
				df1 = pd.read_json(dataset.get(key1))

				ed_directory2 = self.ed_directories[self.directory2]
				dataset2 = ed_directory.get(self.dataset2)
				key2 = dataset.keys()[0]
				df2 = pd.read_json(dataset.get(key2))
				return self.ed_component.statistics(df1, df2)
			elif (self.method == OPTIONS[4]):
				ed_directory1 = self.ed_directories[self.directory1]
				dataset1 = ed_directory.get(self.dataset1)
				key1 = dataset.keys()[0]
				df1 = pd.read_json(dataset.get(key1))

				ed_directory2 = self.ed_directories[self.directory2]
				dataset2 = ed_directory.get(self.dataset2)
				key2 = dataset.keys()[0]
				df2 = pd.read_json(dataset.get(key2))
				return self.ed_component.statistics_columns(df1, df2, self.column1, self.column2)
		except Exception as e:
			# TODO: probably do more about this part, more error handling
			error_message = 'Could not plot, invalid input format. Check these are correct ---> {0} {1} {2}'.format(self.method, self.json_indexes, self.columns)
			raise Exception(error_message)
