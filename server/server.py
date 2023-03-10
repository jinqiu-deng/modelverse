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
    def initialize(self, config):
        self.config = config

    def get(self):
        logging.info('Received GET request from %s', self.request.remote_ip)
        self.render('frontend.html')

    def post(self):
        logging.info('Received POST request from %s', self.request.remote_ip)
        openai.organization = self.config.settings['openai_organization']
        openai.api_key = self.config.settings['openai_api_key']

        data = json.loads(self.request.body.decode('utf-8'))
        question = data['question']
        logging.info('Received question "%s" from %s', question, self.request.remote_ip)

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            #  temperature=0.2,
            #  max_tokens=20,
            messages=[{ "role": "user", "content": question}]
        )

        answer = completion.choices[0].message.content
        logging.info('Generated answer "%s" for question "%s" from %s', answer, question, self.request.remote_ip)
        logging.info('Generated completion "%s" for question "%s" from %s', completion, question, self.request.remote_ip)

        response = {
            'answer': answer
        }

        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(response))

config = Config(os.path.join(os.path.dirname(__file__), "openai_gpt_key.yaml"))

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler, dict(config=config)),
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
