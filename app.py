import re
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Constants
FIFO = "/tmp/led_fifo"

def is_quiet_hours():
    """Returns True if current Eastern Time is between 11 PM and 9 AM."""
    now = datetime.now(ZoneInfo("America/New_York"))
    return now.hour >= 23 or now.hour < 9

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/color', methods=['POST'])
def set_color():
    if is_quiet_hours():
        return jsonify({"error": "LEDs are locked between 11:00 PM and 9:00 AM ET"}), 403

    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    color_hex = data.get('color', '')

    # Must be # followed by exactly 6 hex characters
    if not re.match(r'^#[0-9a-fA-F]{6}$', color_hex):
        return jsonify({"error": "Invalid hex color format"}), 400

    try:
        with open(FIFO, 'w') as fifo:
            fifo.write(f"C:{color_hex}")
        return jsonify({"status": "success", "received": color_hex})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/brightness', methods=['POST'])
def set_brightness():
    if is_quiet_hours():
        return jsonify({"error": "LEDs are locked between 11:00 PM and 9:00 AM ET"}), 403

    data = request.json
    if not data:
         return jsonify({"error": "No data provided"}), 400
         
    brightness = data.get('brightness')
    
    # Validate brightness is between 0 and 255
    if not isinstance(brightness, int) or not (0 <= brightness <= 255):
         return jsonify({"error": "Invalid brightness value"}), 400
         
    try:
        with open(FIFO, 'w') as fifo:
            fifo.write(f"B:{brightness}")
        return jsonify({"status": "success", "received": brightness})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
@app.route('/api/strobe', methods=['POST'])
def toggle_strobe():
    if is_quiet_hours():
        return jsonify({"error": "LEDs are locked between 11:00 PM and 9:00 AM ET"}), 403

    data = request.json
    if data is None:
         return jsonify({"error": "No data provided"}), 400
         
    is_strobing = data.get('strobe', False)
    
    try:
        state = "1" if is_strobing else "0"
        with open(FIFO, 'w') as fifo:
            fifo.write(f"S:{state}")
        return jsonify({"status": "success", "strobe": is_strobing})
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
