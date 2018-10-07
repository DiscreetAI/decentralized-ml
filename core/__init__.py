import asyncio
from ipywidgets import *
from IPython.display import display
from core.category_component import *
from core.db_client import DBClient

def get_category():
    """
    Displays:
        Prompt to get category from user
        ED directories to user or failure with the reason
        Some decoration has been added to this method
    """
    def orchestrate(sender):
        category_text = category_widget.value.strip().lower()
        db_client = DBClient()
        category_component = CategoryComponent(db_client)
        cc_dict = category_component.get_ed_with_category(category_text)
        # more coming here :D

    decoration()
    category_text = None
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
    	A decoration for the notebook, logo of Dagora
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
