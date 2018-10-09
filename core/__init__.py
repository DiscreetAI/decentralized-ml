from ipywidgets import widgets
from IPython.display import display, Image
from core.category_component import CategoryComponent
from core.db_client import DBClient

class Orchestrator(object):
	"""
	ED Directories Class Front-End

	- 
	""" 
	def __init__(self):
		"""
		Initialize EDDirectories instance.
		"""
		self.db_client = DBClient()
		self.category_component = CategoryComponent(db_client)
		self.ed_directories = None

	def get_ed_directories(self):
		"""
		Return ed_directories to the user.
		"""
		return self.ed_directories

	def get_category_name(self):
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
			global ed_directories
			# TODO: change this to the actual value of the dictionary, it should not be jsut the category text
			self.ed_directories = category_text
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
