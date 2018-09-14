import tests.context

import os

import pytest

from core.configuration import ConfigurationManager


if not os.path.isdir('tests/artifacts/config_manager'):
	os.mkdir('tests/artifacts/config_manager')


def check_config_exists(cm):
	""" Ensure that a config file was created using default user input. """
	assert cm.get_config()


def setup_default_worked(cm):
	""" Actually verify that the config file created using default user input is correct. """
	config = cm.get_config()
	assert config.get('GENERAL', 'dataset_path') == 'datasets/mnist'
	assert config.getint('SCHEDULER', 'num_runners') == 4
	assert config.getint('SCHEDULER', 'frequency_in_mins') == 1
	assert config.get('RUNNER', 'weights_directory') == 'weights'


def setup_custom_worked(cm, custom_string):
	""" Actually verify that the config file created using custom user input is correct. """
	config = cm.get_config()
	assert config.get('GENERAL', 'dataset_path') == custom_string
	assert config.get('SCHEDULER', 'num_runners') == custom_string
	assert config.get('SCHEDULER', 'frequency_in_mins') == custom_string
	assert config.get('RUNNER', 'weights_directory') == custom_string

def test_complete_setup_default():
	""" Verify configuration.ini from default user input is created and correct. """
	config_manager = ConfigurationManager()
	config_manager.bootstrap(
		config_filepath='tests/artifacts/config_manager/configuration.ini',
		input_function=lambda x: ''
	)
	check_config_exists(config_manager)
	setup_default_worked(config_manager)
	os.remove(config_manager.config_filepath)


def test_complete_setup_custom():
	""" Verify configuration.ini from custom user input is created and correct. """
	config_manager = ConfigurationManager()
	custom_string = 'test'
	config_manager.bootstrap(
		config_filepath='tests/artifacts/config_manager/configuration2.ini',
		input_function=lambda x: custom_string
	)
	check_config_exists(config_manager)
	setup_custom_worked(config_manager, custom_string)
	os.remove(config_manager.config_filepath)


def test_no_setup_repeat():
	""" Verify that run_setup_mode is not run again when configuration already exists. Or more simply, that the
		configuration has not changed) """
	config_manager = ConfigurationManager()
	config_manager.bootstrap(
		config_filepath='tests/artifacts/config_manager/configuration3.ini',
		input_function=lambda x: ''
	)
	check_config_exists(config_manager)
	assert not config_manager.bootstrap()
	setup_default_worked(config_manager)
	os.remove(config_manager.config_filepath)
