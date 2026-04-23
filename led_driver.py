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

# Initialize Strip
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

def set_color(hex_color):
    """Parses hex and sets strip color with error handling."""
    try:
        hex_color = hex_color.lstrip('#')
        # Robust conversion to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        color = Color(r, g, b)
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, color)
        strip.show()
    except (ValueError, IndexError) as e:
        print(f"Error parsing color '{hex_color}': {e}")

# Create FIFO with restricted permissions if it doesn't exist
# If the pipe exists, remove it to ensure a clean start
if os.path.exists(FIFO):
    os.remove(FIFO)

# Create the pipe
os.mkfifo(FIFO)

# IMPORTANT: Give the web user permission to write to it
# 0o666 makes it readable/writable by everyone locally
os.chmod(FIFO, 0o666)

print("LED Driver is running. Waiting for input...")

try:
    while True:
        # Open the FIFO in read mode; this blocks until data is written
        with open(FIFO, 'r') as fifo:
            data = fifo.read().strip()
            if data:
                set_color(data)
        # Small sleep to prevent high CPU usage if the pipe behaves unexpectedly
        time.sleep(0.01)
finally:
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0,0,0))
    strip.show()

