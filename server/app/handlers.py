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
        self.key_lock = key_lock
        self.key_state = key_state

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
            # Log the total number of requests under processing and the number for each org_id
            total_requests = sum(self.key_state.values())
            logging.info('Total requests under processing: %d', total_requests)
            for org_key, org_requests in self.key_state.items():
                logging.info('Requests under processing for org_id %s: %d', org_key, org_requests)

            # Select the key with the least number of under processing requests
            selected_key_index = min(self.key_state, key=self.key_state.get)
            self.key_state[selected_key_index] += 1

            organization_id = self.config.settings['organizations'][selected_key_index]['id']
            api_key = self.config.settings['organizations'][selected_key_index]['key']
            custom_openai_client = CustomOpenAIClient(organization_id, api_key)

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

        # Decrement the count of under processing requests for the selected key
        async with self.key_lock:
            self.key_state[selected_key_index] -= 1
