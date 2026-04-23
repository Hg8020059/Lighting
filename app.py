import re
from flask import Flask, request, jsonify, render_template
from rpi_ws281x import Adafruit_NeoPixel, Color

app = Flask(__name__)

# --- CONFIG ---
LED_COUNT      = 60      
LED_PIN        = 10      # SPI MOSI
LED_FREQ_HZ    = 800000  
LED_DMA        = 10      
LED_BRIGHTNESS = 150     # Hardcoded mid-range brightness for stability
LED_INVERT     = False   
LED_CHANNEL    = 0       

# Initialize strip
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

def hex_to_color(hex_string):
    hex_string = hex_string.lstrip('#')
    r, g, b = tuple(int(hex_string[i:i+2], 16) for i in (0, 2, 4))
    # Note: Some WS2812 strips use GRB order. 
    # If colors are swapped, change this to Color(g, r, b)
    return Color(r, g, b)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/color', methods=['POST'])
def set_color():
    data = request.json
    color_hex = data.get('color')

    if not color_hex or not re.match(r'^#[0-9A-Fa-f]{6}$', color_hex):
        return jsonify({"error": "Invalid color"}), 400

    target_color = hex_to_color(color_hex)
    
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, target_color)
    
    strip.show()
    return jsonify({"status": "success", "color": color_hex}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)