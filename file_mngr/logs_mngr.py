import logging
import file_mngr.conf_mngr as conf
from datetime import datetime

dt_now = datetime.now().replace(microsecond=0)

if conf.check_path('logs'):
    logging.basicConfig(level=logging.INFO, filename=f'logs/{str(dt_now).replace(":", "-")}.log', filemode='w',
                        format="%(asctime)s %(levelname)s %(message)s")
else:
    conf.create_path('logs')
    logging.basicConfig(level=logging.INFO, filename=f'logs/{str(dt_now).replace(":", "-")}.log', filemode='w',
                        format="%(asctime)s %(levelname)s %(message)s")


def log_info(event):
    logging.info(event)


def log_warning(event):
    logging.warning(event)


def log_error(event):
    logging.error(event)
