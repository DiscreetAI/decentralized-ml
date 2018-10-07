from ipywidgets import widgets
from IPython.display import display, Image
from core.category_component import CategoryComponent
from core.db_client import DBClient

"""
	Global variables
"""
db_client = DBClient()
category_component = CategoryComponent(db_client)


def get_ed_directories():
	"""
	Displays:
		Prompt to get category from user.
		ED directories to user or failure.
	"""
	def orchestrate(sender):
		"""
		This method is triggered by the button.on_click event
    	It uses the current value of category_widget variable
    	to get the dictionary with ed.
		"""
		category_text = category_widget.value.strip().lower()
		cc_dict = category_component.get_ed_with_category(category_text)
		# TODO: should handle the case with cc_dict, failure or success
		# if this is SUCCESS then there should a visualization happening
		# otherwise some failure handler

	category_widget = widgets.Text(
		value=None,
		placeholder='',
		description='Category:',
		disabled=False,

	)
	button = widgets.Button(description='Submit')
	button.on_click(orchestrate)
	display(category_widget)
	display(button)

def decoration():
	"""
	Displays:
		A decoration for the notebook, logo of Dagora.
	"""
	file = open("core/images/DA_nowords.png", "rb")
	image = file.read()
	image_widget = widgets.Image(
		value=image,
		format='png',
		width=300,
		height=400,
	)
	display(image_widget)

