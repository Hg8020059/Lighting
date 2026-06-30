#!/usr/bin/env python3
import time
import argparse
from datetime import datetime
from zoneinfo import ZoneInfo
from rpi_ws281x import *

# LED strip configuration:
LED_COUNT      = 60      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating a signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

def colorWipe(strip, color, wait_ms=50):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)
        
def fill(strip, color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()
    
def flashbang(strip):
    strip.setBrightness(255)
    fill(strip, Color(255, 255, 255))
    time.sleep(0.45)
    for i in range(255, -1, -1):
        strip.setBrightness(i)
        strip.show()
        time.sleep(0.01)

def is_quiet_hours():
    """Returns True if current Eastern Time is between 11 PM and 9 AM."""
    now = datetime.now(ZoneInfo("America/New_York"))
    return now.hour >= 23 or now.hour < 9

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()

    print ('Press Ctrl-C to quit.')

    try:
        # Initial startup sequence
        if not is_quiet_hours():
            flashbang(strip)
            strip.setBrightness(255)
            fill(strip, Color(222, 24, 186))
            
        was_quiet = is_quiet_hours() # Track the state

        while True:
            currently_quiet = is_quiet_hours()
            
            if currently_quiet and not was_quiet:
                # Transitioned into quiet hours: Turn off
                colorWipe(strip, Color(0, 0, 0), 20)
                was_quiet = True
                
            elif not currently_quiet and was_quiet:
                # Transitioned out of quiet hours: Turn on
                strip.setBrightness(255)
                fill(strip, Color(222, 24, 186))
                was_quiet = False
                
            # NOTE: Your logic to actually read from "/tmp/led_fifo" 
            # should go here so the API can control the lights during the day.
                
            time.sleep(1) # Prevents the loop from maxing out CPU usage

    except KeyboardInterrupt:
        colorWipe(strip, Color(0,0,0), 10)
