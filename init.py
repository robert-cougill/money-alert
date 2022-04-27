import json
import logging
import os
import pathlib
import sched
import sys
import time
import util

global coin_list
global config
global email_content
global logger
global project_directory
global scheduler


def init():
    global email_content
    email_content = []

    global project_directory
    project_directory = pathlib.Path(__file__).parent

    load_config()
    set_environment_variables()
    build_coin_list()
    create_report_data_directory()
    create_scheduler()

    import database_util
    database_util.DatabaseHelper().create_database()


def set_environment_variables():
    global logger
    logger = logging.getLogger('money-alert')
    if '--dev' in sys.argv or '--run-now' in sys.argv:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    elif '--build' in sys.argv:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    elif '--daily' in sys.argv:
        logging.basicConfig(filename=util.configure_file_path('/var/log/money-alert-daily.log'), level=config['log_level'], format='%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    elif '--watchers' in sys.argv:
        logging.basicConfig(filename=util.configure_file_path('/var/log/money-alert-watchers.log'), level=config['log_level'], format='%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def load_config():
    global config
    config_path = util.configure_file_path('config.json')
    config_file = open(config_path, 'r')
    config = json.load(config_file)
    config_file.close()


def build_coin_list():
    global coin_list
    coin_list = {key: value for key, value in config['coin_list'].items()}


def create_report_data_directory():
    directory_name = util.configure_file_path('report/report_data')
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
        logger.debug(f'Creating directory: {directory_name}')


def create_scheduler():
    global scheduler
    scheduler = sched.scheduler(time.time, time.sleep)


init()
