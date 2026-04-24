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
        
def strobe():
    """The background loop that rapidly switches lights on and off."""
    global strobe_active, active_color
    off_color = Color(0, 0, 0)
    
    while strobe_active:
        # Turn OFF
        with strip_lock:
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, off_color)
            strip.show()
        time.sleep(0.05) # Pause 50 milliseconds
        
        # Turn ON
        with strip_lock:
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, active_color)
            strip.show()
        time.sleep(0.05) # Pause 50 milliseconds
        
def toggle_strobe(toggle_str):
    #Starts or stops the strobe thread
    global strobe_active, strobe_thread
    
    try:
        is_on = int(toggle_str) == 1
        
        if is_on and not strobe_active:
            # Turn strobe ON
            strobe_active = True
            strobe_thread = threading.Thread(target=strobe)
            strobe_thread.daemon = True # Ensures the thread dies if the main script stops
            strobe_thread.start()
            
        elif not is_on and strobe_active:
            # Turn strobe OFF
            strobe_active = False
            if strobe_thread is not None:
                strobe_thread.join() # Wait for the strobe thread to finish its last sleep cycle
            
            # Ensure the lights are left ON with the correct color
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
    # Open the FIFO once for reading
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
                        toggle_strobe(data[2:0])
        # The 'with' block will only exit if the pipe is closed by the writer
        # We sleep briefly before reopening to prevent CPU spiking
        time.sleep(0.1)
finally:
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0,0,0))
    strip.show()
