import sys
import os
import pprint
import json

# Ensure that the rpi_utils library is in search path
sys.path.append(os.path.dirname(__file__) + '/..')
from rpi_utils import TemperatureSensor

ts = TemperatureSensor()
temps = ts.read_temperature()
pprint.pprint(temps)
