import yaml

class Config:
    def __init__(self, filename):
        with open(filename, 'r') as f:
            self.settings = yaml.load(f, Loader=yaml.FullLoader)
