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
	def getInstance():
		""" Static access method. """
		if ConfigurationManager.__instance == None:
			ConfigurationManager()
		return ConfigurationManager.__instance

	def __init__(self, config_filepath="core/configuration.ini"):
		""" Virtually private constructor. """
		if ConfigurationManager.__instance != None:
			raise Exception("This class is a singleton!")
		else:
			ConfigurationManager.__instance = self
			self.config_filepath = config_filepath
			self.question_format = "{question} [default = {default}] "
			self.config = None

	def bootstrap(self, test_input=None):
		""" Do nothing if config instance already exists. Otherwise, check if core/configuration.ini exists. If not, call 
			run_setup_mode. Then load the config instance from configuration.ini

			'test_input' is just an easy way to mock out user input for testing """
		if not self.config:
			user_input = test_input if test_input else input
			print(os.listdir('core'))
			if not os.path.isfile(self.config_filepath):
				print("found")
				self.run_setup_mode(user_input)
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

	def reset(self):
		""" Used for cleanup during testing"""
		if os.path.isfile(self.config_filepath):
			os.remove(self.config_filepath)








