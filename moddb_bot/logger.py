import logging
import os
from datetime import datetime

import colorlog


def get_console_handler():
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(colorlog.ColoredFormatter(
        '{green}{asctime} {log_color}{levelname} {reset}{name}: {white}{message}',
        log_colors={
            'DEBUG': 'white',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        datefmt='%H:%M:%S',
        style='{'
    ))
    return console_handler


def get_file_handler(path: str):
    logs_dir = '../logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    file_handler = logging.FileHandler(f'../logs/{path}', encoding='utf-8', mode='w')
    file_handler.setFormatter(logging.Formatter(
        '{asctime} {levelname} {name}: {message}',
        datefmt='%H:%M:%S',
        style='{'
    ))
    return file_handler


def setup_logger():
    log = logging.getLogger()
    log.setLevel(logging.INFO)

    log.addHandler(get_console_handler())
    log.addHandler(get_file_handler('latest.log'))

    current_dt = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
    log.addHandler(get_file_handler(f'{current_dt}.log'))

    logging.TRACE = 5
    logging.addLevelName(logging.TRACE, "TRACE")

    logging.getLogger("api").setLevel(logging.DEBUG)
    logging.getLogger("bot").setLevel(logging.DEBUG)
    logging.getLogger("discord_bot").setLevel(logging.DEBUG)
    logging.getLogger("subscription").setLevel(logging.DEBUG)
