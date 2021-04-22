import RPi.GPIO as GPIO
import time
import glob

class TemperatureSensor:
    ''' Interface to a temperature sensor connected to raspberry pi (through 1-wire interface)
        The physical sensor has to be connected and setup for this to work
        
        Example:
            ts = rpi_utils.TemperatureSensor()
            temp = ts.read_temperature()
    '''
    def read_temperature(self):
        ''' Returns current temp in C and F (as a dict)
            { 'temp_c':	2.937,
              'temp_f': 37.2866
            }
        '''
        lines = self._read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self._read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            temps = {'temp_c': temp_c, 'temp_f': temp_f}
            return temps
        else:
            raise ValueError("Couldn't parse temperature file")

    def _read_temp_raw(self):
        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '28*')[0]
        device_file = device_folder + '/w1_slave'
        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
        return  lines

 

class Relay:
    def __init__(self, trig_pin, on_level='HIGH', gpio_mode=GPIO.BCM, gpio_warnings=None):
        self.trig_pin = trig_pin

        if gpio_mode != None: GPIO.setmode(gpio_mode)
        if gpio_warnings != None: GPIO.setwarnings(gpio_warnings)
        
        if on_level == 'HIGH':
            self.on_level = GPIO.HIGH
            self.off_level = GPIO.LOW 
        else:
            self.on_level = GPIO.LOW
            self.off_level = GPIO.HIGH
            
        GPIO.setup(trig_pin, GPIO.OUT)               # Set pin mode to "output"
        GPIO.output(self.trig_pin, self.off_level)   # Ensure relay is "off"

    def on(self):
        ''' Turn relay on '''
        GPIO.output(self.trig_pin, self.on_level)

    def off(self):
        ''' Turn relay off '''
        GPIO.output(self.trig_pin, self.off_level)
        
    def momentary(self, delay=1):
        ''' Make the relay behave like a momentary switch.
            Switch on for a short time and then switch off again
        '''
        self.on()
        time.sleep(delay)
        self.off()

# Code based on https://electrosome.com/hc-sr04-ultrasonic-sensor-raspberry-pi/
class DistanceMeasurer:
    def __init__(self, trig_pin, echo_pin, settle_time=1, range_min=2, range_max=500, gpio_mode=GPIO.BCM, gpio_warnings=None):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.settle_time = settle_time
        self.range_min = range_min
        self.range_max = range_max
        
        if gpio_mode != None: GPIO.setmode(gpio_mode)
        if gpio_warnings != None: GPIO.setwarnings(gpio_warnings)

        GPIO.setup(trig_pin, GPIO.OUT)
        GPIO.setup(echo_pin, GPIO.IN)

    # This may not be a good idea as the object could go out of scope while the rest of the calling program
    # is still using GPIO port. Better handled by the calling program
    #def __del__(self):
    #    GPIO.cleanup()

    def cleanup(self):
        GPIO.cleanup()

    def get_dist(self):
        GPIO.output(self.trig_pin, False)               #Set trig_pin as LOW
        #print "Waiting For Sensor To Settle"
        time.sleep(self.settle_time)                    #Delay of 2 seconds

        GPIO.output(self.trig_pin, True)                #Set trig_pin as HIGH
        time.sleep(0.00001)                             #Delay of 0.00001 seconds
        GPIO.output(self.trig_pin, False)               #Set trig_pin as LOW

        trig_time = time.time()
        while GPIO.input(self.echo_pin)==0:             #Check whether the echo_pin is LOW
            pulse_start = time.time()                   #Saves the last known time of LOW pulse
            if pulse_start - trig_time > 5:             # TImeout in 5 seconds
                raise RuntimeError ("Timeout waiting for echo signal.")
            
        while GPIO.input(self.echo_pin)==1:             #Check whether the echo_pin is HIGH
            pulse_end = time.time()                     #Saves the last known time of HIGH pulse 

        pulse_duration = pulse_end - pulse_start        #Get pulse duration to a variable

        distance = pulse_duration * 17150               #Multiply pulse duration by 17150 to get distance
        distance = round(distance, 2)                   #Round to two decimal points

        return distance

        #if distance > self.range_min and distance < self.range_max:      #Check whether the distance is within range
        #    #print "Distance:",distance - 0.5,"cm"  #Print distance with 0.5 cm calibration
        #    return distance
        #else:
        #    raise RuntimeError ("Out Of Range %f" % distance)                   #display out of range

    def get_dist_with_check(self, retry_time=0.25):
        dist = None
        max_tries = 4
        while max_tries > 0:
            dist = self.get_dist()
            # wait a little and get distance again
            time.sleep (retry_time)
            dist1 = self.get_dist()
            # Value is valid only if both values are similar
            if abs(dist1-dist) < 5 and dist > self.range_min and dist < self.range_max:
                break
            max_tries -= 1
        return dist

class RGBled:
    def __init__(self, red, green, blue, hz=100, gpio_mode=GPIO.BCM, gpio_warnings=None, start_pwm=False):
        self.red = red
        self.green = green
        self.blue = blue
        self.hz = hz

        if gpio_mode != None: GPIO.setmode(gpio_mode)
        if gpio_warnings != None: GPIO.setwarnings(gpio_warnings)
        
        GPIO.setup (red, GPIO.OUT)
        GPIO.setup (green, GPIO.OUT)
        GPIO.setup (blue, GPIO.OUT)

        GPIO.output (red, GPIO.LOW)
        GPIO.output (green, GPIO.LOW)
        GPIO.output (blue, GPIO.LOW)

        self.red_pwm   = GPIO.PWM (red,   hz)
        self.green_pwm = GPIO.PWM (green, hz)
        self.blue_pwm  = GPIO.PWM (blue,  hz)

        if start_pwm:
            # Start PWM with duty cycle 0 (off)
            self.start_pwm(dc=0)

    def start_pwm (self, dc=0):
        self.blue_pwm.start(dc)
        self.green_pwm.start(dc)
        self.red_pwm.start(dc)

    def stop_pwm (self):
        self.blue_pwm.stop()
        self.green_pwm.stop()
        self.red_pwm.stop()

    def __del__(self):
        self.stop_pwm()

    def color_red(self, exclusive=True):
        self.stop_pwm()
        if exclusive:
            self.off()
        GPIO.output (self.red, GPIO.HIGH)

    def color_green(self, exclusive=True):
        self.stop_pwm()
        if exclusive:
            self.off()
        GPIO.output (self.green, GPIO.HIGH)

    def color_blue(self, exclusive=True):
        self.stop_pwm()
        if exclusive:
            self.off()
        GPIO.output (self.blue, GPIO.HIGH)

    def off(self):
        self.stop_pwm()
        GPIO.output (self.red, GPIO.LOW)
        GPIO.output (self.green, GPIO.LOW)
        GPIO.output (self.blue, GPIO.LOW)
    
    def change_colors(self, dc_r, dc_g, dc_b, delay=0):
        '''Change the duty cycle of each LED's PWM to values specified
            If a value is None, the DC will remain unchanged
        '''
        
        if dc_r != None : self.red_pwm.ChangeDutyCycle(dc_r) 
        if dc_g != None : self.green_pwm.ChangeDutyCycle(dc_g)
        if dc_b != None : self.blue_pwm.ChangeDutyCycle(dc_b)
        
        time.sleep (delay)

    def cycle_colors(self, delay=0.01):
        '''Cycle through different color combinations'''
        for i in range(100):
            self.change_colors(None, 100-i, i, delay=delay)

        for i in range(100):
            self.change_colors(i, None, 100-i, delay=delay)

        for i in range(100):
            self.change_colors(100-i, i/2, None, delay=delay)


    def PosSinWave(self, amplitude, angle, frequency):
        ''' Adapted from http://www.henryleach.com/2013/05/controlling-rgb-led-with-raspberry-pi.html
        '''
        #angle in degrees  
        #creates a positive sin wave between 0 and amplitude*2  
        return amplitude + (amplitude * math.sin(math.radians(angle)*frequency) )  

    def change_colors_sin(self):
        try:  
            while 1:  
                for i in range(0, 720, 5):  
                    self.change_colors( self.PosSinWave(50, i, 0.5),  
                                        self.PosSinWave(50, i, 1),  
                                        self.PosSinWave(50, i, 2),  
                                        delay = 0.1 )  
       
        except KeyboardInterrupt:  
            pass  


##############################################################################################################

if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    
#     trig_pin = 15                                       #Associate pin 18 to trig_pin
#     echo_pin = 18                                       #Associate pin 23 to echo_pin
#     dm = DistanceMeasurer(trig_pin, echo_pin)
#     print "Distance measurement in progress"
#     while True:
#         try:
#             dist = dm.get_dist()
#             print 'Distance is %f' % dist
#         except RuntimeError, e:
#             print 'ERROR: %s' % e
#         except KeyboardInterrupt:
#             GPIO.cleanup()   
# 	    exit(0)

    led = RGBled(23, 25, 7)
    led.color_red()
    time.sleep(1)
    led.color_blue()
    time.sleep(1)
    led.color_green()
    time.sleep(1)
    led.off()
    #led.start_pwm()
    #led.change_colors(50, 5, 5)
    #time.sleep(2)
    #led.cycle_colors()
    #time.sleep(2)
#    
#    for i in range(3):
#        led.cycle_colors(delay=0.01)
#
#    print "Sin Wave"
#    led.change_colors_sin()


    relay = Relay(24)
    print("on")
    relay.on()
    time.sleep(2)
    print("off")
    relay.off()
    time.sleep(2)
    GPIO.cleanup()
         
        

