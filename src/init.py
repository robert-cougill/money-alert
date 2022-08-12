import json
import logging
import os
import pathlib
import re
import sched
import sys
import time
import util

global coin_list
global config
global email_content
global logger
global money_alert_arrow_down
global money_alert_arrow_up
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
    global money_alert_arrow_down
    money_alert_arrow_down = os.getenv('MONEY_ALERT_ARROW_DOWN')
    global money_alert_arrow_up
    money_alert_arrow_up = os.getenv('MONEY_ALERT_ARROW_UP')
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
    with open(config_path, 'r') as config_file:
        replacements = {
            "API_BITTREX_KEY": os.getenv('API_BITTREX_KEY'),
            "API_BITTREX_SECRET": os.getenv('API_BITTREX_SECRET'),
            "API_ALPHA_VANTAGE_KEY": os.getenv('API_ALPHA_VANTAGE_KEY'),
            "API_METAL_PRICE_KEY": os.getenv('API_METAL_PRICE_KEY'),
            "MONEY_ALERT_EMAIL_SECRET": os.getenv('MONEY_ALERT_EMAIL_SECRET'),
            "MONEY_ALERT_EMAIL_USERNAME": os.getenv('MONEY_ALERT_EMAIL_USERNAME'),
            "PERSONAL_EMAILS": os.getenv('PERSONAL_EMAILS')
        }
        replacements = dict((re.escape(k), v) for k, v in replacements.items())
        pattern = re.compile("|".join(replacements.keys()))
        config = json.loads(pattern.sub(lambda m: replacements[re.escape(m.group(0))], config_file.read()))


def build_coin_list():
    global coin_list
    coin_list = {key: value for key, value in config['coin_list'].items()}


def create_report_data_directory():
    directory_name = util.configure_file_path('report/report_data/charts')
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
        logger.debug(f'Creating directory: {directory_name}')


def create_scheduler():
    global scheduler
    scheduler = sched.scheduler(time.time, time.sleep)


init()
