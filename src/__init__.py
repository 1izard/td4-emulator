import json
import os
from enum import Enum

config_path = os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), 'TD4_config.json')
with open(config_path, 'r') as f:
    CONFIG = json.load(f)


class ClockCycle(Enum):
    NORMAL = 1  # 1 Hz
    HIGH = 10   # 10 Hz
    MANUAL = 0  # Manual
