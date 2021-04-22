import flask
import sys
import os
import pprint
import json

# Ensure that the rpi_utils library is in search path
sys.path.append(os.path.dirname(__file__) + '/..')
from rpi_utils import TemperatureSensor

application = flask.Flask(__name__)

@application.route('/')
def temperature():
    '''' Use the rpi_utils libary to get temperature.
         Returns a jsonified dictionary containing temperature in C and F
    '''
    ts = TemperatureSensor()
    temps = ts.read_temperature()
    return flask.jsonify(temps)

if __name__ == '__main__':
    # For testing from command line
    with application.app_context():
        pprint.pprint(temperature().get_data())
