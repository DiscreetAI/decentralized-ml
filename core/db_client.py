from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json
import pandas as pd
import os
import time
import logging


logging.basicConfig(level=logging.DEBUG,
                    format='[DBClient] %(asctime)s %(levelname)s %(message)s')

class DBClient(object):
	"""
	DBClient

	- Label datasets and retrieve datasets with corresponding category
	- Needed here so that DL2 Notebook can retrieve classifications
	- Unsure whether DL2 Notebook will use this DBClient (through Virtual 
	  Worker instance of UNIX Service) or have its own instance, TBD
	- Will most likely replace RDS DB with DynamoDB for performance reasons, 
	  but I'll figure that out after MVP

	TODO: authenthication needs to be set up for DB
	"""
	def __init__(self, config_manager):
		"""
		Set up DBClient with corresponding database credentials
		"""
		config = config_manager._config
		app = Flask(__name__)
		app.config['SQLALCHEMY_DATABASE_URI'] =  \
			'postgresql://{user}:{pw}@{host}:{port}/{db}'.format(
				user=config.get('DB_CLIENT', 'user'),
				pw=os.environ['DB_PASS'],
				host=config.get('DB_CLIENT', 'host'),
				port=config.getint('DB_CLIENT', 'port'),
				db=config.get('DB_CLIENT', 'db')
			)
		app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
		self.db = SQLAlchemy(app)
		self.table_name = config.get('DB_CLIENT', 'table_name')
		self.num_tries = config.getint('DB_CLIENT', 'max_tries')
		self.wait_time = config.getint('DB_CLIENT', 'wait_time')

	def _get_classifications(self):
		"""
		Get category_labels table

		NOTE: Functionality needs to be tested so that add_classifications can be
		tested, but this method should not be used for the UNIX Service. Will 
		be used for DL2 Notebook.
		"""
		query = "select * from {table_name}".format(table_name=self.table_name)
		for _ in range(self.num_tries):
			try:
				return pd.read_sql_query(query, self.db.engine)
			except Exception as e:
				logging.error(e)
				time.sleep(self.wait_time)
				continue
		raise Exception('Getting classifications failed.')

	def add_classifications(self, data_providers, categories):
		"""
		Append new category classifications to the category_labels table and replace old
		classifications, where categories[i] corresponds to the labeled category for 
		data_providers[i]
		"""
		classifications = self._get_classifications()
		index = classifications.index
		classifications = classifications.set_index('data_provider')
		for data_provider, category in zip(data_providers, categories):
			classifications.loc[data_provider] = category
		classifications['data_provider'] = classifications.index
		classifications.index = list(range(len(classifications.index)))
		for _ in range(self.num_tries):
			try:
				classifications.to_sql(
					name=self.table_name,
					con=self.db.engine,
					if_exists='replace',
					index=False
				)
				return
			except Exception as e:
				logging.error(e)
				time.sleep(self.wait_time)
				continue
		raise Exception('Adding classifications failed.')
		

	def _get_data_providers_with_category(self, category):
		"""
		Get a list of data providers with the given category.
		
		NOTE: Functionality needs to be tested so that add_classifications can be 
		tested, but this method should not be used for the UNIX Service. Will 
		be used for DL2 Notebook.
		"""
		query = "select * from {table_name} where category = '{category}'".format(
			category=category, 
			table_name=self.table_name
		)
		for _ in range(self.num_tries):
			try:
				return pd.read_sql_query(query, self.db.engine)
			except Exception as e:
				logging.error(e)
				time.sleep(self.wait_time)
				continue
		raise Exception('Getting classifications failed.')
		
		
