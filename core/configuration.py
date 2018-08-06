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
	def get_instance(config_filepath="core/configuration.ini", input_function=None):
		""" Static access method. Always call this to get an instance of the class."""
		input_function = input_function if input_function else input
		if not ConfigurationManager.__instance:
			ConfigurationManager(config_filepath, input_function)
		else:
			ConfigurationManager.__instance.config_filepath = config_filepath
			ConfigurationManager.__instance.input_function = input_function
			ConfigurationManager.__instance.config = None
		ConfigurationManager.__instance.bootstrap()
		return ConfigurationManager.__instance

	def __init__(self, config_filepath, input_function):
		""" Virtually private constructor. """
		if ConfigurationManager.__instance != None:
			raise Exception("This class is a singleton!")
		else:
			ConfigurationManager.__instance = self
			self.config_filepath = config_filepath
			self.question_format = "{question} [default = {default}] "
			self.config = None
			self.input_function = input_function if input_function else input


	def bootstrap(self):
		""" Do nothing if config instance already exists. Otherwise, check if core/configuration.ini exists. If not, call 
			run_setup_mode. Then load the config instance from configuration.ini

			'test_input' is just an easy way to mock out user input for testing """
		if not self.config:
			if not os.path.isfile(self.config_filepath):
				self.run_setup_mode(self.input_function)
			self.config = configparser.ConfigParser()
			self.config.read(self.config_filepath)


	def run_setup_mode(self, user_input):
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