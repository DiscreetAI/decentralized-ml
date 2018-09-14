from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json
import pandas as pd
import os
import time


class DBClient(object):
	"""
	DBClient

	- Label datasets and retrieve datasets with corresponding category
	- Needed here so that DL2 Notebook can retrieve labels
	- Unsure whether DL2 Notebook will use this DBClient (through Virtual Worker instance of UNIX Service) or have its own instance, TBD
	- Will most likely replace RDS DB with DynamoDB for performance reasons, but I'll figure that out after MVP

	TODO: authenthication needs to be set up for DB
	"""
	def __init__(self, config_filepath = 'database_config.json'):
		"""
		Set up DBClient with corresponding database credentials
		"""
		app = Flask(__name__)
		with open(config_filepath) as f:
			db_config = json.load(f)
		db_config['pw'] = os.environ['DB_PASS']
		app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % db_config
		app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
		self.db = SQLAlchemy(app)
		self.table_name = db_config['table_name']
		self.num_tries = db_config['num_tries']
		self.wait_time = db_config['wait_time']

	def get_labels(self):
		"""
		Get category_labels table
		"""
		for _ in range(self.num_tries):
			try:
				return pd.read_sql_query("select * from {table_name}".format(table_name=self.table_name), self.db.engine)
			except Exception as e:
				time.sleep(self.wait_time)
				continue
		raise Exception('Getting labels failed.')

	def add_labels(self, data_providers, categories):
		"""
		Append new category labels to the category_labels table and replace old labels, where categories[i] corresponds 
		to the labeled category for data_providers[i]
		"""
		labels = self.get_labels()
		index = labels.index
		labels = labels.set_index('data_provider')
		for data_provider, category in zip(data_providers, categories):
			labels.loc[data_provider] = category
		labels['data_provider'] = labels.index
		labels.index = list(range(len(labels.index)))
		for _ in range(self.num_tries):
			try:
				labels.to_sql(name=self.table_name, con=self.db.engine, if_exists='replace', index=False)
				return
			except Exception as e:
				time.sleep(self.wait_time)
				continue
		raise Exception('Adding labels failed.')
		

	def get_data_providers_with_category(self, category):
		"""
		Get a list of data providers with the given category.
		"""
		for _ in range(self.num_tries):
			try:
				return pd.read_sql_query("select * from {table_name} where category = '{category}'"
					.format(category=category, table_name=self.table_name), self.db.engine)
			except Exception as e:
				time.sleep(self.wait_time)
				continue
		raise Exception('Adding labels failed.')
		
		
