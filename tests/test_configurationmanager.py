import tests.context
import pytest
import mock
from core.configuration import ConfigurationManager


cm = ConfigurationManager()

def setup_default_sanity():
	""" Ensure that a config file was created using default user input. """
	cm.bootstrap(test_input=lambda x: '')
	assert cm.config

def setup_default_worked():
	""" Actually verify that the config file created using default user input is correct. """
	config = cm.config
	assert config.get('GENERAL', 'dataset_path') == 'datasets/mnist'
	assert config.getint('SCHEDULER', 'num_runners') == 4
	assert config.getint('SCHEDULER', 'frequency_in_mins') == 1
	assert config.get('RUNNER', 'weights_directory') == 'weights'

def setup_custom_sanity():
	""" Ensure that a config file was created using custom user input. """
	cm.bootstrap(test_input=lambda x: 'test')
	assert cm.config

def setup_custom_worked():
	""" Actually verify that the config file created using custom user input is correct. """
	config = cm.config
	assert config.get('GENERAL', 'dataset_path') == 'test'
	assert config.get('SCHEDULER', 'num_runners') == 'test'
	assert config.get('SCHEDULER', 'frequency_in_mins') == 'test'
	assert config.get('RUNNER', 'weights_directory') == 'test'

def test_complete_setup_default():
	""" Verify configuration.ini from default user input is created and correct. """
	cm.reset()
	setup_default_sanity()
	setup_default_worked()

def test_complete_setup_custom():
	""" Verify configuration.ini from custom user input is created and correct. """
	cm.reset()
	setup_custom_sanity()
	setup_custom_worked()

def test_no_setup_repeat():
	""" Verify that run_setup_mode is not run again when configuration already exists. Or more simply, that the 
		configuration has not changed) """
	cm.reset()
	cm.bootstrap(test_input=lambda x: '')
	setup_default_worked()
	cm.bootstrap(test_input=lambda x: 'test')
	setup_default_worked()
