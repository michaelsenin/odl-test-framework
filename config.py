import ConfigParser

import yaml

CONFIG_NAME = 'config.cfg'


class Config(object):

    def __init__(self):
        config = ConfigParser.RawConfigParser(allow_no_value=True)
        config.readfp(open(CONFIG_NAME))
        self.items = {}
        for section in config.sections():
            self.items[section] = dict(config.items(section))

    @staticmethod
    def _finditem(obj, key):
        if key in obj:
            return obj[key]
        for k, v in obj.items():
            if isinstance(v, dict):
                item = Config._finditem(v, key)
                if item is not None:
                    return item

    def __getattr__(self, name):
        return yaml.load(Config._finditem(self.items, name))
