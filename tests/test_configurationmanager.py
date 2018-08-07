import tests.context
import pytest
import mock
import os
from core.configuration import ConfigurationManager


@pytest.fixture
def my_cm():
	if not os.path.isdir('tests/artifacts/config_manager'):
		os.mkdir('tests/artifacts/config_manager')

	if ConfigurationManager.has_instance():
		ConfigurationManager.get_instance().config = None
		ConfigurationManager.get_instance().config_filepath = 'tests/artifacts/config_manager/configuration.ini'
		ConfigurationManager.get_instance().input_function = lambda x: ''
		ConfigurationManager.get_instance().bootstrap()
	else:
		ConfigurationManager(config_filepath='tests/artifacts/config_manager/configuration.ini', 
							 input_function=lambda x: '')

def setup_default_sanity(cm):
	""" Ensure that a config file was created using default user input. """
	assert cm.config

def setup_default_worked(cm):
	""" Actually verify that the config file created using default user input is correct. """
	config = cm.config
	assert config.get('GENERAL', 'dataset_path') == 'datasets/mnist'
	assert config.getint('SCHEDULER', 'num_runners') == 4
	assert config.getint('SCHEDULER', 'frequency_in_mins') == 1
	assert config.get('RUNNER', 'weights_directory') == 'weights'

def setup_custom_sanity(cm):
	""" Ensure that a config file was created using custom user input. """
	assert cm.config

def setup_custom_worked(cm):
	""" Actually verify that the config file created using custom user input is correct. """
	config = cm.config
	assert config.get('GENERAL', 'dataset_path') == 'test'
	assert config.get('SCHEDULER', 'num_runners') == 'test'
	assert config.get('SCHEDULER', 'frequency_in_mins') == 'test'
	assert config.get('RUNNER', 'weights_directory') == 'test'

def test_complete_setup_default(my_cm):
	""" Verify configuration.ini from default user input is created and correct. """
	cm = ConfigurationManager.get_instance()
	cm.run_setup_mode('tests/artifacts/config_manager/configuration.ini', lambda x: '')
	setup_default_sanity(cm)
	setup_default_worked(cm)
	os.remove(cm.config_filepath)
	assert not os.path.isfile('tests/artifacts/config_manager/configuration.ini')

def test_complete_setup_custom():
	""" Verify configuration.ini from custom user input is created and correct. """
	cm = ConfigurationManager.get_instance()
	cm.run_setup_mode('tests/artifacts/config_manager/configuration.ini', lambda x: 'test')
	setup_custom_sanity(cm)
	setup_custom_worked(cm)
	os.remove(cm.config_filepath)
	assert not os.path.isfile('tests/artifacts/config_manager/configuration.ini')

def test_no_setup_repeat():
	""" Verify that run_setup_mode is not run again when configuration already exists. Or more simply, that the 
		configuration has not changed) """
	cm = ConfigurationManager.get_instance()
	cm.run_setup_mode('tests/artifacts/config_manager/configuration.ini', lambda x: '')
	setup_default_worked(cm)
	assert not cm.bootstrap()
	setup_default_worked(cm)
	os.remove(cm.config_filepath)
	assert not os.path.isfile('tests/artifacts/config_manager/configuration.ini')
