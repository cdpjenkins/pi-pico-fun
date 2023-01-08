import os
import gc
import random
from urllib import urequest

from pimoroni import ShiftRegister
from picographics import PicoGraphics, DISPLAY_INKY_FRAME
from machine import Pin, SPI
import jpegdec
from network_manager import NetworkManager
import uasyncio

import WIFI_CONFIG

import sdcard
import uos

def setup_sd_card():
    sd_spi = SPI(0, sck=Pin(18, Pin.OUT), mosi=Pin(19, Pin.OUT), miso=Pin(16, Pin.OUT))
    sd = sdcard.SDCard(sd_spi, Pin(22))
    os.mount(sd, "/sd")
    gc.collect()
    
def status_handler(mode, status, ip):
    print(mode, status, ip)
    
def connect_network():
    network_manager = NetworkManager(WIFI_CONFIG.COUNTRY, status_handler=status_handler)
    uasyncio.get_event_loop().run_until_complete(network_manager.client(WIFI_CONFIG.SSID, WIFI_CONFIG.PSK))
    gc.collect()

FILENAME = "/sd/placekitten.jpg"

def load_placekitten():
    # url = "http://placekitten.com/600/448"
    url = "{}/bichinho.jpg".format(WIFI_CONFIG.IMAGES_URL)

    print("loading image from {}".format(url))

    socket = urequest.urlopen(url)
    data = bytearray(1024)
    with open(FILENAME, "wb") as f:
        while True:
            if socket.readinto(data) == 0:
                break
            f.write(data)
    socket.close()
    gc.collect()

    jpeg = jpegdec.JPEG(display)
    gc.collect()

display = PicoGraphics(display=DISPLAY_INKY_FRAME)

setup_sd_card()
connect_network()
load_placekitten()

# and the activity LED
activity_led = Pin(6, Pin.OUT)

# set up and enable vsys hold so we don't go to sleep
HOLD_VSYS_EN_PIN = 2

hold_vsys_en_pin = Pin(HOLD_VSYS_EN_PIN, Pin.OUT)
hold_vsys_en_pin.value(True)

# Create a new JPEG decoder for our PicoGraphics
j = jpegdec.JPEG(display)

def display_image(filename):
    activity_led.on()
    j.open_file(filename)
    j.decode(0, 0, jpegdec.JPEG_SCALE_FULL)
    display.update()
    activity_led.off()
    gc.collect()
    
display_image(FILENAME)
