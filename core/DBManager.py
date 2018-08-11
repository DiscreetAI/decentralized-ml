from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json
import pandas as pd


class DBManager(object):

	def __init__(self, config_filepath = 'database_config.json'):
		app = Flask(__name__)
		with open(config_filepath) as f:
			POSTGRES = json.load(f)
		app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
		self.db = SQLAlchemy(app)
		self.table_name = POSTGRES['table_name']
		self._reset()

	def get_labels(self):
		return pd.read_sql_query("select * from {table_name}".format(table_name=self.table_name), self.db.engine)

	def add_labels(self, data_providers, categories):
		rows = {'data_provider': data_providers, 'category': categories} 
		label = pd.DataFrame(data=rows)
		label.to_sql(name=self.table_name, con=self.db.engine, if_exists='append', index=False)

	def get_data_providers_with_category(self, category):
		return pd.read_sql_query("select * from {table_name} where category = '{category}'"
			.format(category=category, table_name=self.table_name), self.db.engine)

	def _reset(self):
		label = pd.DataFrame(columns=['data_provider', 'category'])
		label.to_sql(name=self.table_name, con=self.db.engine, if_exists='replace', index=False)
		
