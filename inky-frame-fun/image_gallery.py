import os
import gc
import random
import time
from urllib import urequest

import jpegdec
from machine import Pin, SPI
from network_manager import NetworkManager
from pimoroni import ShiftRegister
from picographics import PicoGraphics, DISPLAY_INKY_FRAME
import sdcard
import uasyncio
import uos

import WIFI_CONFIG

def enable_vsys_hold_to_prevent_sleep():
    HOLD_VSYS_EN_PIN = 2

    hold_vsys_en_pin = Pin(HOLD_VSYS_EN_PIN, Pin.OUT)
    hold_vsys_en_pin.value(True)

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

def load_text_from_url(url):
    connection = urequest.urlopen(url)
    contents = connection.read()
    connection.close()
    return contents.strip().decode("utf-8")

def download_image(filename):
    url = "{}/{}".format(WIFI_CONFIG.IMAGES_URL, filename)

    print("downloading image from {}".format(url))

    socket = urequest.urlopen(url)
    data = bytearray(1024)
    path_on_sd = f"/sd/{filename}"
    with open(path_on_sd, "wb") as f:
        while True:
            if socket.readinto(data) == 0:
                break
            f.write(data)
    socket.close()
    url = None
    gc.collect()

def download_images():
    for image_file in images_list:
        download_image(image_file)

def display_image(filename):
    path_on_sd = f"/sd/{filename}"
    
    print(f"Opening {path_on_sd}")
    
    activity_led.on()
    display.set_pen(1)
    display.clear()
    j.open_file(path_on_sd)
    j.decode(0, 0, jpegdec.JPEG_SCALE_FULL)
    display.update()
    activity_led.off()
    gc.collect()
    
def show_slideshow():
    while True:
        for image_file in images_list:
            display_image(image_file)
            time.sleep(60)


display = PicoGraphics(display=DISPLAY_INKY_FRAME)
j = jpegdec.JPEG(display)
activity_led = Pin(6, Pin.OUT)

enable_vsys_hold_to_prevent_sleep()
setup_sd_card()
connect_network()

images_list = load_text_from_url("{}/list.txt".format(WIFI_CONFIG.IMAGES_URL)).split("\n")
print([image_file for image_file in images_list])

print("Images downloaded")
print(gc.mem_free())
