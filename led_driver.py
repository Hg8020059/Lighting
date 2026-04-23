#!/usr/bin/env python3
import os
import time
from rpi_ws281x import Adafruit_NeoPixel, Color

# LED Configuration
LED_COUNT      = 60
LED_PIN        = 18
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 80
LED_INVERT     = False
LED_CHANNEL    = 0
FIFO           = "/tmp/led_fifo"

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

def set_color(hex_color):
    #Parses hex and sets strip color.
    try:
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        color = Color(r, g, b)
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, color)
        strip.show()
    except (ValueError, IndexError) as e:
        print(f"Error parsing color '{hex_color}': {e}")

def set_brightness(level_str):
    #Parses integer string and sets strip brightness.
    try:
        level = int(level_str)
        strip.setBrightness(level)
        strip.show()
    except ValueError as e:
        print(f"Error parsing brightness '{level_str}': {e}")

# FIFO Setup
if os.path.exists(FIFO):
    os.remove(FIFO)
os.mkfifo(FIFO)
os.chmod(FIFO, 0o666)

print("LED Driver is running. Waiting for input...")

try:
    while True:
        with open(FIFO, 'r') as fifo:
            data = fifo.read().strip()
            if data:
                # Check prefixes to determine which function to call
                if data.startswith("C:"):
                    set_color(data[2:])
                elif data.startswith("B:"):
                    set_brightness(data[2:])
        time.sleep(0.01)
finally:
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0,0,0))
    strip.show()