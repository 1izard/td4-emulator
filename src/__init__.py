import json
import os

config_path = os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), 'TD4_config.json')
with open(config_path, 'r') as f:
    CONFIG = json.load(f)
