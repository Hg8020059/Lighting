import time
import re
from flask import Flask, request, jsonify, render_template
from rpi_ws281x import *

app = Flask(__name__)

# --- LED STRIP CONFIGURATION ---
LED_COUNT      = 60      # Number of LED pixels.
LED_PIN        = 10      # SPI MOSI pin
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz
LED_DMA        = 10      # DMA channel
LED_BRIGHTNESS = 100     # Default brightness
LED_INVERT     = False   
LED_CHANNEL    = 0       

# Initialize the LED strip globally so it stays active
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

# --- HARDWARE FUNCTIONS ---
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

# Helper function to convert Hex colors (#RRGGBB) to WS281x Color objects
def hex_to_color(hex_string):
    hex_string = hex_string.lstrip('#')
    r, g, b = tuple(int(hex_string[i:i+2], 16) for i in (0, 2, 4))
    return Color(r, g, b)

# --- WEB ROUTES ---

@app.route('/')
def index():
    # Serves the HTML frontend
    return render_template('index.html')

@app.route('/api/flashbang', methods=['POST'])
def trigger_flashbang():
    flashbang(strip)
    return jsonify({"status": "Flashbang deployed!"}), 200

@app.route('/api/brightness', methods=['POST'])
def set_brightness():
    data = request.json
    brightness = data.get('brightness')

    # STRICT VALIDATION: Ensure it's an integer between 0 and 255
    try:
        brightness = int(brightness)
        if brightness < 0 or brightness > 255:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid brightness value"}), 400

    strip.setBrightness(brightness)
    strip.show()
    return jsonify({"status": "success", "brightness": brightness}), 200

@app.route('/api/color', methods=['POST'])
def set_color():
    data = request.json
    color_hex = data.get('color')

    # STRICT VALIDATION: Ensure it is a perfectly formatted 7-character hex string
    if not color_hex or not re.match(r'^#[0-9A-Fa-f]{6}$', color_hex):
        return jsonify({"error": "Invalid color format"}), 400

    led_color = hex_to_color(color_hex)
    fill(strip, led_color)
    return jsonify({"status": "success", "color": color_hex}), 200

if __name__ == '__main__':
    # Only used for local testing. In production, use Gunicorn.
    app.run(host='0.0.0.0', port=5000)
