import flask
import sys
import os
import pprint
import json

# Ensure that the rpi_utils library is in search path
sys.path.append(os.path.dirname(__file__) + '/..')
from rpi_utils import DistanceMeasurer

application = flask.Flask(__name__)
application.debug = True

@application.route('/')
def distance():
    '''' Use the rpi_utils libary to get measured distance from the ultrasonic sensor.
         Returns a number in cm
    '''
    trig_pin = 15
    echo_pin = 18
    dm = DistanceMeasurer(trig_pin, echo_pin)
    distance = dm.get_dist_with_check()
    return distance

if __name__ == '__main__':
    # For testing from command line
    with application.app_context():
        pprint.pprint(distance().get_data())
