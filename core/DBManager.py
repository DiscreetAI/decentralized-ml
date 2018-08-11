from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json
import pandas as pd


class DBManager(object):
	__instance = None

	@staticmethod
	def get_instance():
		return __instance

	def __init__(self, config_filepath = 'database_config.json'):
		if DBManager.__instance:
			raise Exception("This class is a singleton!")
		else:
			DBManager.__instance = self
		app = Flask(__name__)
		with open(config_filepath) as f:
			POSTGRES = json.load(f)
		app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
		self.db = SQLAlchemy(app)

	def get_labels(self):
		try:
			labels = pd.read_sql_query("select * from category_labels", self.db.engine)
			return labels
		except:
			raise Exception('Table "category_labels" does not exist!')

	def add_label(self, data_provider, category):
		row = {
			'data_provider': [data_provider],
			'category': [category]
		}
		labels = pd.DataFrame(data=row)
		labels.to_sql(name='category_labels', con=self.db.engine, if_exists='append', index=False)

	def get_data_providers_with_category(self, category):
		try:
			query = "select * from category_labels where category = '{category}'".format(category=category)
			return list(pd.read_sql_query(query, self.db.engine)['data_provider'])
		except:
			raise Exception('Table "category_labels" does not exist!')

	def _reset(self):

		labels = pd.DataFrame(columns=['data_provider', 'category'])
		labels.to_sql(name='category_labels', con=self.db.engine, if_exists='replace', index=False)
		
