import json

# Config loading
CONFIG = json.load(open("config.json", "r"))


def get(key):
    """Get a value from the config file"""
    return CONFIG.get(key, None)
