import re
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

def hex_to_color(hex_string):
    hex_string = hex_string.lstrip('#')
    r, g, b = tuple(int(hex_string[i:i+2], 16) for i in (0, 2, 4))
    # Note: Some WS2812 strips use GRB order. 
    # If colors are swapped, change this to Color(g, r, b)
    return Color(r, g, b)

@app.route('/')
def index():
    return render_template('index.html')

FIFO = "/tmp/led_fifo"

@app.route('/api/color', methods=['POST'])
def set_color():
    data = request.json
    color_hex = data.get('color')

    if not color_hex:
        return jsonify({"error": "Invalid"}), 400

    with open(FIFO, 'w') as fifo:
        fifo.write(color_hex)

    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
