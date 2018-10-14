from ipywidgets import widgets
from IPython.display import display, Image
from core.category_component import CategoryComponent
from core.db_client import DBClient
import pandas as pd
from core.ed_component import EDComponent

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
		self.json_indexes = []
		self.columns = []
		self.method = None
 
	def get_ed_directories(self):
		"""
		Return ed_directories to the user.
		"""
		return self.ed_directories

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

	def directories_indexes(self):
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
				self.json_indexes = [int(index.strip()) for index in directories_widget.value.split(',')]
				self.columns = [column.strip() for column in columns_widget.value.split(',')]
				# TODO: handle visualization
				sender.disabled = False

			directories_widget = widgets.Text(
				value=None,
				placeholder='',
				description='Directories:',
				disabled=False,

			)
			columns_widget = widgets.Text(
				value=None,
				placeholder='',
				description='Columns:',
				disabled=False,

			)
			method_widget = widgets.RadioButtons(
			    options=['histogram', 'scatter', 'compare using histograms', 'describe numerical'],
			    value='histogram',
			    description='Method:',
			    disabled=False
			)
			button = widgets.Button(description='Submit')
			display(method_widget)
			display(directories_widget)
			display(columns_widget)
			display(button)
			button.on_click(store)

	def visualize(self): 
		"""
		Returns the corresponding plot.
		"""
		try: 
			if (self.method == 'histogram'):
				df = pd.read_json(self.ed_directories[self.json_indexes[0]])
				column = self.columns[0]
				return self.ed_component.histogram(df, column)
			elif (self.method == 'scatter'):
				df1 = pd.read_json(self.ed_directories[self.json_indexes[0]])
				# df2 = pd.read_json(self.ed_directories[self.json_indexes[1]])
				column1 = self.columns[0]
				column2 = self.columns[1]
				return self.ed_component.scatter(df1, column1, column2)
			elif (self.method == 'compare using histograms'):
				df1 = pd.read_json(self.ed_directories[self.json_indexes[0]])
				df2 = pd.read_json(self.ed_directories[self.json_indexes[1]])
				column1 = self.columns[0]
				column2 = self.columns[1]
				return self.ed_component.compare_using_histograms(df1, df2, column1, column2)
			elif (self.method == 'describe numerical'):
				df1 = pd.read_json(self.ed_directories[self.json_indexes[0]])
				df2 = pd.read_json(self.ed_directories[self.json_indexes[1]])
				column1 = self.columns[0]
				column2 = self.columns[1]
				return self.ed_component.describe(df1, df2, column1, column2)
		except Exception as e:
			# TODO: probably do more about this part, more error handling
			error_message = 'Could not plot, invalid input format. Check these are correct ---> {0} {1} {2}'.format(self.method, self.json_indexes, self.columns)
			raise Exception(error_message)
