# coding=utf-8

import tornado.ioloop
import tornado.web
import yaml
import os
import openai
import json
import logging
import datetime
from logging.handlers import RotatingFileHandler
import pytz
from tornado.platform.asyncio import AsyncIOMainLoop
from threading import Lock

class Config:
    def __init__(self, filename):
        with open(filename, 'r') as f:
            self.settings = yaml.load(f, Loader=yaml.FullLoader)

class BeijingFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, tz=None):
        super().__init__(fmt, datefmt)
        self.tz = tz or pytz.timezone('Asia/Shanghai')

    def formatTime(self, record, datefmt=None):
        dt = datetime.datetime.fromtimestamp(record.created, tz=pytz.utc)
        return dt.astimezone(self.tz).strftime(datefmt)

class MainHandler(tornado.web.RequestHandler):
    def initialize(self, config, key_lock):
        self.config = config
        self.key_lock = key_lock
        self.key_index = 0

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()

    def get(self):
        logging.info('Received GET request from %s', self.request.remote_ip)
        self.render('frontend.html')

    async def post(self):
        logging.info('Received POST request from %s', self.request.remote_ip)

        with self.key_lock:
            openai.organization = self.config.settings['organizations'][self.key_index]['id']
            openai.api_key = self.config.settings['organizations'][self.key_index]['key']

            self.key_index = (self.key_index + 1) % len(self.config.settings['organizations'])

        data = json.loads(self.request.body.decode('utf-8'))
        logging.info('Received question "%s" from %s', data, self.request.remote_ip)

        # Filter out properties that are not defined in data
        chat_completion_args = {
            key: value for key, value in data.items() if key in {
                'model', 'messages', 'temperature', 'top_p', 'n', 'max_tokens',
                'presence_penalty', 'frequency_penalty', 'user', 'logit_bias'}
        }

        completion = openai.ChatCompletion.create(**chat_completion_args)

        answer = completion.choices[0].message.content
        logging.info('Generated answer "%s" for question "%s" from %s', answer, data['messages'][-1]['content'], self.request.remote_ip)
        logging.info('Generated completion "%s" for question "%s" from %s', completion, data, self.request.remote_ip)

        response = {
            'completion': completion.to_dict()
        }

        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(response))

config = Config(os.path.join(os.path.dirname(__file__), "openai_gpt_key.yaml"))

key_lock = Lock()

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler, dict(config=config, key_lock=key_lock)),
    ])

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, 'server.log')

    formatter = BeijingFormatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S %z')
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=100, encoding="utf-8")
    file_handler.setFormatter(formatter)

    logging.getLogger('').addHandler(file_handler)

    app = make_app()
    app.listen(8080, address="0.0.0.0")
    logging.info('Started server')
    tornado.ioloop.IOLoop.current().start()
