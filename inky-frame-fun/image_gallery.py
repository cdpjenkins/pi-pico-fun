from pimoroni import ShiftRegister
from picographics import PicoGraphics, DISPLAY_INKY_FRAME
from machine import Pin
import jpegdec

# set up the display
display = PicoGraphics(display=DISPLAY_INKY_FRAME)

# and the activity LED
activity_led = Pin(6, Pin.OUT)

# set up and enable vsys hold so we don't go to sleep
HOLD_VSYS_EN_PIN = 2

hold_vsys_en_pin = Pin(HOLD_VSYS_EN_PIN, Pin.OUT)
hold_vsys_en_pin.value(True)

# Create a new JPEG decoder for our PicoGraphics
j = jpegdec.JPEG(display)

# setup
activity_led.on()

def display_image(filename):
    j.open_file(filename)
    j.decode(0, 0, jpegdec.JPEG_SCALE_FULL)
    display.update()

display_image("bichinhos_scaled.jpg")


