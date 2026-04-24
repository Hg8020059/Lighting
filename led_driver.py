#!/usr/bin/env python3
import os
import time
import threading
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

# Global state for threading
strip_lock = threading.Lock()     # Prevents simultaneous hardware access
strobe_active = False             # Control flag for the strobe loop
strobe_thread = None              # Thread handle
active_color = Color(0, 255, 0)   # Current color state

def set_color(hex_color):
    global active_color
    try:
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        active_color = Color(r, g, b)
        with strip_lock:
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, active_color)
            strip.show()
    except (ValueError, IndexError) as e:
        print(f"Error parsing color '{hex_color}': {e}")

def set_brightness(level_str):
    try:
        level = int(level_str)
        with strip_lock:
            strip.setBrightness(level)
            strip.show()
    except ValueError as e:
        print(f"Error parsing brightness '{level_str}': {e}")
        
def strobe():
    global strobe_active, active_color
    off_color = Color(0, 0, 0)
    
    while strobe_active:
        # Flash OFF
        with strip_lock:
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, off_color)
            strip.show()
        time.sleep(0.05)
        
        # Flash ON
        with strip_lock:
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, active_color)
            strip.show()
        time.sleep(0.05)
        
def toggle_strobe(toggle_str):
    global strobe_active, strobe_thread
    try:
        # Convert the string value from FIFO to an integer
        is_on = int(toggle_str) == 1
        
        if is_on and not strobe_active:
            strobe_active = True
            strobe_thread = threading.Thread(target=strobe)
            strobe_thread.daemon = True
            strobe_thread.start()
            
        elif not is_on and strobe_active:
            strobe_active = False
            if strobe_thread:
                strobe_thread.join()
            
            # Reset to steady color after strobe stops
            with strip_lock:
                for i in range(strip.numPixels()):
                    strip.setPixelColor(i, active_color)
                strip.show()
                
    except ValueError as e:
        print(f"Error parsing strobe toggle '{toggle_str}': {e}")

# FIFO Setup
if os.path.exists(FIFO):
    os.remove(FIFO)
os.mkfifo(FIFO)
os.chmod(FIFO, 0o666)

print("LED Driver is running. Waiting for input...")

try:
    while True:
        with open(FIFO, 'r') as fifo:
            for line in fifo:
                data = line.strip()
                if data:
                    if data.startswith("C:"):
                        set_color(data[2:])
                    elif data.startswith("B:"):
                        set_brightness(data[2:])
                    elif data.startswith("S:"):
                        # Corrected slice from [2:0] to [2:] to get the value
                        toggle_strobe(data[2:]) 
        time.sleep(0.1)
finally:
    with strip_lock:
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0,0,0))
        strip.show()