import subprocess
import time, os
import pioled
from board import SCL, SDA
import busio
from adafruit_seesaw.seesaw import Seesaw   #soil sensor library
from Adafruit_IO import Client, Feed
#from PIL import Image, ImageDraw, ImageFont
import RPi.GPIO as GPIO
from secrets import secrets

#get IP address for display
cmd = "hostname -I | cut -d\' \' -f1"
IP = subprocess.check_output(cmd, shell=True).decode("utf-8")

button = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(button, GPIO.IN,GPIO.PUD_UP)


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

def button_pressed(channel):
    print("shutting down")
    pioled.display_textlines(["Shutting Down  "])
    os.system("sudo shutdown -h now")
    time.sleep(5)

#button state is interrupt driven and is not polled.
GPIO.add_event_detect(button, GPIO.FALLING,callback=button_pressed,bouncetime=200)

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

# Main Program

print("starting program")
pioled.display_textlines(["Starting Up"])
time.sleep(2)


while True:
    temp, touch = read_sensor()
    print_data(temp,touch)
    pioled.display_textlines(["Temp: "+str(temp),
                              "Moisture: "+str(touch),
                              "IP: "+IP])
    send_data_to_Adafruit_io(temp,touch)
    time.sleep(FEED_TIMEOUT)