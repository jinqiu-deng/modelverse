import os
import tornado.ioloop
from tornado.web import Application
from app.config import Config
from app.handlers import MainHandler
from app.logging_config import setup_logging
from threading import Lock
import asyncio
from setproctitle import setproctitle
from tornado.web import StaticFileHandler

setproctitle("modelverse_server")

config = Config(os.path.join(os.path.dirname(__file__), "openai_gpt_key.yaml"))
key_lock = asyncio.Lock()
key_state = {}
for group in config.settings['groups']:
    group_name = group['name']
    key_state[group_name] = {i: 0 for i in range(len(group['keys']))}

def make_app():
    static_path = os.path.join(os.path.dirname(__file__), 'templates')

    return Application([
        (r"/", MainHandler, dict(config=config, key_lock=key_lock, key_state=key_state)),
        (r"/static/(.*)", StaticFileHandler, {"path": static_path}),
    ])

if __name__ == "__main__":
    setup_logging()  # Sets up logging configuration
    app = make_app()
    app.listen(8888, address="0.0.0.0")
    tornado.ioloop.IOLoop.current().start()
