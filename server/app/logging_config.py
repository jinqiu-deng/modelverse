import logging
import datetime
import pytz
from logging.handlers import RotatingFileHandler
import os

class BeijingFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, tz=None):
        super().__init__(fmt, datefmt)
        self.tz = tz or pytz.timezone('Asia/Shanghai')

    def formatTime(self, record, datefmt=None):
        dt = datetime.datetime.fromtimestamp(record.created, tz=pytz.utc)
        return dt.astimezone(self.tz).strftime(datefmt)

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, 'server.log')

    formatter = BeijingFormatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S %z')
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=100, encoding="utf-8")
    file_handler.setFormatter(formatter)

    logging.getLogger('').addHandler(file_handler)
