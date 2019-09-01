# soilsensor
Python code for raspberry pi which uses the Adafruit STEMMA soil sensor, a display and sends the temperature and moisture data to Adafruit IO

There are two versions of the code, written for 2 different diplays:

1) Uses pioled display (link: https://www.adafruit.com/product/3527)
This code calls the pioled.py library
A button is connected to GPIO21 to shutdown the PI for use in headless mode.

2) Uses pi ZeroSeg 8x7seg+2xbuttons phat from PiHut (link: https://thepihut.com/products/zeroseg)
This code uses a state machine to determine the course of action for each button press, including
-waiting
-measuring
-shutdown confirm
-shutdown 

