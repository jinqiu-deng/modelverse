#coding=utf-8

import tornado.ioloop
import tornado.web
import yaml
import os
import openai
import json

class Config:
    def __init__(self, filename):
        with open(filename, 'r') as f:
            self.settings = yaml.load(f, Loader=yaml.FullLoader)

class MainHandler(tornado.web.RequestHandler):
    def initialize(self, config):
        self.config = config

    def get(self):
        self.render('frontend.html')

    def post(self):
        openai.organization = self.config.settings['openai_organization']
        openai.api_key = self.config.settings['openai_api_key']

        data = json.loads(self.request.body.decode('utf-8'))
        question = data['question']

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.2,
            max_tokens=20,
            messages=[{ "role": "user", "content": question}]
        )

        answer = completion.choices[0].message.content

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
    app = make_app()
    app.listen(8080, address="0.0.0.0")
    tornado.ioloop.IOLoop.current().start()
