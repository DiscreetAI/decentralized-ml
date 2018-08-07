import os
import json
import pandas as pd
import configparser
import logging


logging.basicConfig(level=logging.DEBUG,
					format='[ConfigurationManager] %(asctime)s %(levelname)s %(message)s')

class ConfigurationManager(object):
	"""
	Configuration Manager

	Singleton class that manages the configuration of all other modules.

	"""

	__instance = None

	@staticmethod
	def get_instance():
		"""
		Static access method. Always call this to get an instance of the class.
		"""
		if not ConfigurationManager.__instance:
			ConfigurationManager()
		return ConfigurationManager.__instance


	def __init__(self):
		"""
		Virtually private constructor.
		"""
		if ConfigurationManager.__instance != None:
			raise Exception("This class is a singleton. Please use get_instance().")
		else:
			self.question_format = "{question} [default = {default}] "
			self._config = None
			ConfigurationManager.__instance = self

	def reset(self):
		"""
		Resets the configuration by deleting it. Bootstrap must be called so that
		the class works as intended.
		"""
		self._config = None
		return self

	def bootstrap(self, config_filepath="core/configuration.ini", input_function=None):
		"""
		Do nothing if config instance already exists. Otherwise, check if
		core/configuration.ini exists. If not, call run_setup_mode. Then load
		the config instance from configuration.ini
		"""
		if self._config:
			return False
		self.input_function = input_function if input_function else input
		self.config_filepath = config_filepath
		if not os.path.isfile(self.config_filepath):
			self.run_setup_mode(self.config_filepath, self.input_function)
		else:
			self._config = configparser.ConfigParser()
			self._config.read(self.config_filepath)
		return True


	def run_setup_mode(self, config_filepath, user_input):
		"""
		Create configuration.ini with the user_input function. In testing,
		this is a deterministic lambda function.
		Otherwise, the user_input function actually draws upon user input.
		"""
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
		self._config = config


	def get_config(self):
		"""
		Returns the configuration.
		"""
		if not self._config:
			raise Exception("Configuration Manager needs to be bootstrapped first.")
		return self._config
