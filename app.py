import re
import os
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Constants
FIFO = "/tmp/led_fifo"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/color', methods=['POST'])
def set_color():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    color_hex = data.get('color', '')

    # STRICT VALIDATION: Must be # followed by exactly 6 hex characters
    if not re.match(r'^#[0-9a-fA-F]{6}$', color_hex):
        return jsonify({"error": "Invalid hex color format"}), 400

    try:
        # Write to FIFO only if validation passes
        with open(FIFO, 'w') as fifo:
            fifo.write(color_hex)
        return jsonify({"status": "success", "received": color_hex})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
