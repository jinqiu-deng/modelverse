import tornado.web
import json
import logging
import openai
import os

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
        self.render(os.path.join(os.path.dirname(__file__), '..', 'templates', 'chatbot.html'))

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
