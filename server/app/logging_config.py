import logging
import datetime
import pytz
from logging.handlers import RotatingFileHandler
import os

class CustomFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, tz=None):
        super().__init__(fmt, datefmt)
        self.tz = tz or pytz.utc

    def formatTime(self, record, datefmt=None):
        dt = datetime.datetime.fromtimestamp(record.created, tz=pytz.utc)
        return dt.astimezone(self.tz).strftime(datefmt)

def setup_logging(timezone='Asia/Shanghai'):
    log_format = '%(asctime)s %(levelname)s %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S %z'
    formatter = CustomFormatter(fmt=log_format, datefmt=date_format, tz=pytz.timezone(timezone))

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logging.basicConfig(level=logging.INFO, handlers=[console_handler])

    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, 'server.log')

    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=100, encoding="utf-8")
    file_handler.setFormatter(formatter)

    logging.getLogger('').addHandler(file_handler)
