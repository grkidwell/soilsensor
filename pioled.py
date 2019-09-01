
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont

import adafruit_ssd1306

i2c_bus = busio.I2C(SCL, SDA)

# Create the SSD1306 OLED class.
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c_bus)

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

def cleardisplay():
    disp.fill(0)
    disp.show()

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Load default font.
#font = ImageFont.load_default()

def fontsize_spacing(list):
    lines = len(list)
    spacinglist = [0,5,3,1]
    spacing = spacinglist[lines-1]
    vfontsize = (bottom-spacing*(lines-1))//lines
    hfontsize = int((2*width)//max([len(text) for text in list]))
    return [min([vfontsize,hfontsize]), spacing]

def display_textline(start_y,fontsize,text):
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', fontsize)
    draw.text((x, start_y), text, font=font, fill=255)

def display_textlines(list):
    fontsize, spacing = fontsize_spacing(list)
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    for y, text in enumerate(list):
        start_y=top+(fontsize+spacing)*y
        display_textline(start_y,fontsize,text)
    disp.image(image)
    disp.show()