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

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.2,
            max_tokens=20,
            messages=[
                {"role": "user", "content": "Redmi Note 10 Pro 5G 天玑1100旗舰芯 67W快充 120Hz旗舰变速金刚屏 幻青 8GB+128GB 智能手机 小米红米8GB+128GB 幻青 \n 小米Redmi Note10Pro 5G游戏智能手机 天玑1100旗舰芯 67W快充 机身颜色:幻青$$存储容量:6GB+128GB$$套餐类型:官方标配$ \n same sku?"}
            ]
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
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
