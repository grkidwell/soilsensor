
import time, os
from board import SCL, SDA
import busio
from adafruit_seesaw.seesaw import Seesaw   #soil sensor library
from Adafruit_IO import Client, Feed
import ZeroSeg.led as led
import RPi.GPIO as GPIO
from secrets import secrets

# Adafruit IO setup
ADAFRUIT_IO_KEY = secrets['aio_key']
ADAFRUIT_IO_USERNAME = secrets['aio_user']
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

temperature_feed = aio.feeds('soiltemp')
moisture_feed    = aio.feeds('soilmoisture')

# Delay in-between sensor readings, in seconds.
FEED_TIMEOUT = 5

# soil sensor setup
i2c_bus = busio.I2C(SCL, SDA)
ss = Seesaw(i2c_bus, addr=0x36)

# Pihut ZeroSeg Display and button setup
device = led.sevensegment(cascaded=2)
leftbutton = 17
rightbutton = 26
GPIO.setmode(GPIO.BCM)
GPIO.setup(leftbutton, GPIO.IN)
GPIO.setup(rightbutton, GPIO.IN)

# State Machine setup
'''
inputs to change states:
  LB - Left Button
  RB - Right Button

states and transitions:
  1.Waiting to take data or shut down
    LB - goto measure
    RB - goto sdconfirm
  2.Measure data
    LB - goto wait
    RB - goto wait
  3.Shutdown confirm
    LB - goto shutdown
    RB - goto wait
  4.Shutdown
'''

WAIT, MEASURE, SDCONFIRM, SHUTDOWN = range(4)
state = MEASURE

#A left or right button press will result in a state transition
#based on the map {dictionary} defined for that button.
#      present state: destination state
LB_state_map = {WAIT: MEASURE,
             MEASURE: WAIT,
           SDCONFIRM: SHUTDOWN}
RB_state_map = {WAIT: SDCONFIRM,
             MEASURE: WAIT,
           SDCONFIRM: WAIT}

# Set up interrupt handler for button press
def button_pressed(channel):
    global state
    if channel == leftbutton:
        state = LB_state_map[state]
    else:
        state = RB_state_map[state]

GPIO.add_event_detect(leftbutton, GPIO.FALLING,callback=button_pressed,bouncetime=200)
GPIO.add_event_detect(rightbutton, GPIO.FALLING,callback=button_pressed,bouncetime=200)

# Input/Output functions
def read_sensor():
    moisture = ss.moisture_read()
    temperature = int(ss.get_temp())
    return [temperature, moisture]

def print_data(temp,touch):
    print("temp: " + str(temp) + "  moisture: " + str(touch))

def send_data_to_Adafruit_io(temp,touch):
    soiltemp = '%.2f'%(temp)
    soilmoisture = '%.2f'%(touch)
    try:
        aio.send(temperature_feed.key, str(soiltemp))
        aio.send(moisture_feed.key, str(soilmoisture))
    except:
        print("failed to connect to Adafruit io server")
        time.sleep(5)

def write_led(temp,touch):
    text = str(temp)+'c '+str(touch)
    device.write_text(1,text)

# State Machine handlers
def handle_wait_state():
    device.write_text(1,"RUN Y N")
    print("waiting for button press")
    time.sleep(5)

def handle_measure_state():
    temp, touch = read_sensor()
    print_data(temp,touch)
    write_led(temp,touch)
    send_data_to_Adafruit_io(temp,touch)
    time.sleep(FEED_TIMEOUT)

def handle_sdconfirm_state():
    print("Are you sure you want to shut down?")
    device.write_text(1,"sd Y N")
    time.sleep(5)

def handle_shutdown():
    print("shutting down")
    device.write_text(1,"OFF")
    os.system("sudo shutdown -h now")

# Main Program
print("starting program")
while True:
    if state == WAIT:
        handle_wait_state()
    elif state == MEASURE:
        handle_measure_state()
    elif state == SDCONFIRM:
        handle_sdconfirm_state()
    elif state == SHUTDOWN:
        handle_shutdown()
        break
    time.sleep(0.2)