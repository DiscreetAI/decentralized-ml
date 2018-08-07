import os
import json
import pandas as pd
import configparser
import logging


logging.basicConfig(level=logging.DEBUG,
					format='[ConfigurationManager] %(asctime)s %(levelname)s %(message)s')

class ConfigurationManager(object):
	__instance = None

	@staticmethod
	def has_instance():
		return ConfigurationManager.__instance

	@staticmethod
	def get_instance():
		""" Static access method. Always call this to get an instance of the class."""
		if not ConfigurationManager.__instance:
			ConfigurationManager()
		return ConfigurationManager.__instance

	def __init__(self, config_filepath="core/configuration.ini", input_function=None):
		""" Virtually private constructor. """
		if ConfigurationManager.__instance != None:
			raise Exception("This class is a singleton!")
		else:
			ConfigurationManager.__instance = self
			self.config_filepath = config_filepath
			self.question_format = "{question} [default = {default}] "
			self.config = None
			self.input_function = input_function if input_function else input
			self.bootstrap()


	def bootstrap(self):
		""" Do nothing if config instance already exists. Otherwise, check if core/configuration.ini exists. If not, call 
			run_setup_mode. Then load the config instance from configuration.ini

			Returns True if new config object was created (for testing) """
		if not self.config:
			if not os.path.isfile(self.config_filepath):
				self.run_setup_mode(self.config_filepath, self.input_function)
			else:
				self.config = configparser.ConfigParser()
				self.config.read(self.config_filepath)
			return True
		return False


	def run_setup_mode(self, config_filepath, user_input):
		""" Create configuration.ini with the user_input function. In testing, this is a deterministic lambda function. 
			Otherwise, the user_input function actually draws upon user input. """
		config = configparser.ConfigParser()
		rows = [r[1] for r in pd.read_csv("core/questions.csv").iterrows()]
		for row in rows:
			question, section, key, default = row['question'], row['section'], row['key'], row['default']
			answer = user_input(self.question_format.format(question=question, default=default))
			answer = answer if answer else default
			if not section in config:
				config[section] = {}
			config[section][key] = answer
		with open(self.config_filepath, 'w') as configfile:
			config.write(configfile)
		self.config = config