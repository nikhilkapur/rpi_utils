import sys
import os
import pprint
import json

# Ensure that the rpi_utils library is in search path
sys.path.append(os.path.dirname(__file__) + '/..')
from rpi_utils import TemperDistanceMeasureratureSensor

trig_pin = 15
echo_pin = 18
dm = DistanceMeasurer(trig_pin, echo_pin)
distance = dm.get_dist_with_check()

pprint.pprint(distance)
