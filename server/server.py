#coding=utf-8

import tornado.ioloop
import tornado.web
import yaml
import os
import openai

class Config:
    def __init__(self, filename):
        with open(filename, 'r') as f:
            self.settings = yaml.load(f, Loader=yaml.FullLoader)

class MainHandler(tornado.web.RequestHandler):
    def initialize(self, config):
        self.config = config

    def get(self):
        openai.organization = self.config.settings['openai_organization']
        openai.api_key = self.config.settings['openai_api_key']

        question = self.get_argument('question')

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.2,
            max_tokens=20,
            messages=[{ "role": "user", "content": question}]
        )

        print(completion)
        self.write(completion)


config = Config(os.path.join(os.path.dirname(__file__), "openai_gpt_key.yaml"))

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler, dict(config=config)),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8080, address="0.0.0.0")
    tornado.ioloop.IOLoop.current().start()
