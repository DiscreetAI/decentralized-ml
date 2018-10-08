from ipywidgets import widgets
from IPython.display import display, Image
from core.category_component import CategoryComponent
from core.db_client import DBClient

"""
	Global variables
"""
db_client = DBClient()
category_component = CategoryComponent(db_client)
ed_directories = None

def get_ed_directories():
	"""
	Return ed_directories to the user.
	"""
	return ed_directories

def get_category_name():
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
		cc_dict = category_component.get_ed_with_category(category_text)
		global ed_directories
		# TODO: change this to the actual value of the dictionary
		ed_directories = None
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
