import datetime
import hashlib
import hmac
import init
import os
import time
import typing


def signature(message: str, salt: str) -> str:
    return hmac.new(salt.encode(), message.encode(), hashlib.sha512).hexdigest()


def sha512(message: str) -> str:
    return hashlib.sha512(message.encode()).hexdigest()


def timestamp() -> int:
    return int(time.time() * 1000)


def convert_satoshis_to_btc(value: int) -> float:
    return value / 100000000


def dict_to_tuple(value: dict, use_keys=False) -> tuple:
    tuple_list = []
    for (k, v) in value.items():
        if use_keys:
            tuple_list.append(k)
            continue

        tuple_list.append(v)

    return tuple(tuple_list)


def to_string(value: typing.Any) -> typing.Optional[str]:
    if isinstance(value, str):
        return value

    from enum import Enum
    if isinstance(value, Enum):
        value = value.value

    return str(value)


def get_report_run_time(report_run_time: str) -> int:
    """ This function provides time in seconds between now and when you want to run your reports """
    run_time = report_run_time.split(':')
    run_hour = int(run_time[0])
    run_minute = int(run_time[1])

    now = datetime.datetime.now()
    wait_time_in_seconds = int((datetime.timedelta(hours=24) - (now - now.replace(hour=run_hour, minute=run_minute, second=0, microsecond=0))).total_seconds() % (24 * 3600))

    return wait_time_in_seconds


def configure_file_path(file_location: str):
    return os.path.join(init.project_directory, file_location)


def list_chart_files(directory: str):
    return os.listdir(directory)


def remove_charts_from_directory(directory: str):
    files = list_chart_files(directory)
    for file in files:
        os.remove(directory + file)
