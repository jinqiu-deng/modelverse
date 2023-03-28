import tornado.web
from tornado.web import RequestHandler
import asyncio
import json
import logging
import openai
import os
from .utils import CustomOpenAIClient

class MainHandler(tornado.web.RequestHandler):
    def initialize(self, config, key_lock, key_state):
        self.config = config
        self.key_state = key_state
        self.key_lock = key_lock

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
        async with self.key_lock:
            organization_id = self.config.settings['organizations'][self.key_state['index']]['id']
            api_key = self.config.settings['organizations'][self.key_state['index']]['key']
            custom_openai_client = CustomOpenAIClient(organization_id, api_key)

            self.key_state['index'] = (self.key_state['index'] + 1) % len(self.config.settings['organizations'])

        request_body_json = json.loads(self.request.body.decode('utf-8'))

        logging.info('Sending question "%s" from %s using org_id %s',
                     request_body_json, self.request.remote_ip, custom_openai_client.organization_id)

        completion = await custom_openai_client.create_chat_completion(request_body_json)

        answer = completion['choices'][0]['message']['content']

        logging.info('Generated completion "%s" for question "%s" from %s using org_id %s',
                     completion, request_body_json, self.request.remote_ip, custom_openai_client.organization_id)

        response = {
            'completion': completion
        }

        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(response))
