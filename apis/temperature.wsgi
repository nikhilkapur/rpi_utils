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
def temp():
    '''' Use the rpi_utils libary to get temperature.
         Returns a jsonified dictionary containing temperature in C and F
    '''
    ts = TemperatureSensor()
    temp_c, temp_f = ts.read_temp()
    temps = {'temp_c': temp_c, 'temp_f': temp_f}
    return flask.jsonify(temps)

if __name__ == '__main__':
    # For testing from command line
    with application.app_context():
        pprint.pprint(temp().get_data())
