import tests.context

import os

import pytest

from core.configuration import ConfigurationManager


if not os.path.isdir('tests/artifacts/config_manager'):
    os.mkdir('tests/artifacts/config_manager')

def check_config_exists(cm):
    """
    Ensure that a config file was created using default user input.
    """
    assert cm.get_config()

def comments_test(config_filepath):
    """
    Check that comments were added to secret sections
    """
    secret_sections = ['DB_CLIENT']
    secret_section_message = "; DO NOT MODIFY THIS SECTION"
    with open(config_filepath, "r") as f:
        lines = [line.strip() for line in f.readlines()]
        for secret_section in secret_sections:
            assert lines[lines.index("[{}]".format(secret_section)) - 1] == secret_section_message

def setup_default_worked(cm):
    """
    Actually verify that the config file created using default user input is correct.
    """
    config = cm.get_config()
    assert config.get('GENERAL', 'dataset_path') == 'datasets/mnist'
    assert config.getint('SCHEDULER', 'num_runners') == 4
    assert config.getint('SCHEDULER', 'frequency_in_mins') == 1
    assert config.get('RUNNER', 'weights_directory') == 'weights'
    assert config.get('DB_CLIENT', 'user') == 'datashark'
    assert config.get('DB_CLIENT', 'db') == 'datasharkdb'
    assert config.get('DB_CLIENT', 'host') == 'datasharkdatabase.cwnzqu4zi2kl.us-west-1.rds.amazonaws.com'
    assert config.getint('DB_CLIENT', 'port') == 5432
    assert config.get('DB_CLIENT', 'table_name') == 'category_labels'
    assert config.getint('DB_CLIENT', 'max_tries') == 3
    assert config.getint('DB_CLIENT', 'wait_time') == 10

def setup_custom_worked(cm, custom_string):
    """
    Actually verify that the config file created using custom user input is correct.
    """
    config = cm.get_config()
    assert config.get('GENERAL', 'dataset_path') == custom_string
    assert config.get('SCHEDULER', 'num_runners') == custom_string
    assert config.get('SCHEDULER', 'frequency_in_mins') == custom_string
    assert config.get('RUNNER', 'weights_directory') == custom_string

def verify_secret_section_values(cm, secret_section):
    """
    Verify that values in DB_CLIENT and DB_CLIENT_2 still have assigned values
    """
    config = cm.get_config()
    assert config.get(secret_section, 'user') == 'datashark'
    assert config.get(secret_section, 'db') == 'datasharkdb'
    assert config.get(secret_section, 'host') == 'datasharkdatabase.cwnzqu4zi2kl.us-west-1.rds.amazonaws.com'
    assert config.get(secret_section, 'port') == '5432'
    assert config.get(secret_section, 'table_name') == 'category_labels'
    assert config.getint(secret_section, 'max_tries') == 3
    assert config.getint(secret_section, 'wait_time') == 10

def test_complete_setup_default():
    """
    Verify configuration.ini from default user input is created and correct.
    """
    config_manager = ConfigurationManager()
    config_manager.bootstrap(
        config_filepath='tests/artifacts/config_manager/configuration.ini',
        input_function=lambda x: ''
    )
    check_config_exists(config_manager)
    setup_default_worked(config_manager)
    verify_secret_section_values(config_manager,'DB_CLIENT')
    comments_test('tests/artifacts/config_manager/configuration.ini')
    os.remove(config_manager.config_filepath)


def test_complete_setup_custom():
    """
    Verify configuration.ini from custom user input is created and correct.
    """
    config_manager = ConfigurationManager()
    custom_string = 'test'
    config_manager.bootstrap(
        config_filepath='tests/artifacts/config_manager/configuration2.ini',
        input_function=lambda x: custom_string
    )
    check_config_exists(config_manager)
    setup_custom_worked(config_manager, custom_string)
    verify_secret_section_values(config_manager,'DB_CLIENT')
    comments_test('tests/artifacts/config_manager/configuration2.ini')
    os.remove(config_manager.config_filepath)


def test_no_setup_repeat():
    """
    Verify that run_setup_mode is not run again when configuration already
    exists. Or more simply, that the configuration has not changed) 
    """
    config_manager = ConfigurationManager()
    config_manager.bootstrap(
        config_filepath='tests/artifacts/config_manager/configuration3.ini',
        input_function=lambda x: ''
    )
    check_config_exists(config_manager)
    assert not config_manager.bootstrap()
    setup_default_worked(config_manager)
    verify_secret_section_values(config_manager, 'DB_CLIENT')
    os.remove(config_manager.config_filepath)

def test_multiple_secret_sections():
    config_manager = ConfigurationManager()
    config_manager.bootstrap(
        config_filepath='tests/artifacts/config_manager/configuration4.ini',
        question_filepath='tests/artifacts/config_manager/questions.csv',
        input_function=lambda x: ''
    )
    check_config_exists(config_manager)
    setup_default_worked(config_manager)
    verify_secret_section_values(config_manager, 'DB_CLIENT')
    verify_secret_section_values(config_manager, 'DB_CLIENT_2')
    comments_test('tests/artifacts/config_manager/configuration4.ini')
    os.remove(config_manager.config_filepath)