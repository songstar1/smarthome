from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import time
import os

app = Flask(__name__)
socketio = SocketIO(app)

device_state = {
    "temperature": 25.0,
    "humidity": 50.0,
    "humanDetect": 0,
    "light": 0,
    "alarm": 0,
    "mode": "normal",
    "lastUpdate": ""
}
pending_command = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update', methods=['POST'])
def update():
    global device_state, pending_command
    data = request.get_json()
    if data:
        device_state.update(data)
        device_state['lastUpdate'] = time.strftime("%H:%M:%S")
        socketio.emit('state_update', device_state)
    cmd = pending_command
    pending_command = None
    return jsonify({"cmd": cmd})

@app.route('/command', methods=['POST'])
def command():
    global pending_command
    cmd_data = request.get_json()
    if cmd_data:
        pending_command = cmd_data
        return jsonify({"status": "ok"})
    return jsonify({"status": "error"}), 400

if __name__ == '__main__':from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import time
import os

app = Flask(__name__)
socketio = SocketIO(app)

device_state = {
    "temperature": 25.0,
    "humidity": 50.0,
    "humanDetect": 0,
    "light": 0,
    "alarm": 0,
    "mode": "normal",
    "lastUpdate": ""
}
pending_command = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update', methods=['POST'])
def update():
    global device_state, pending_command
    data = request.get_json()
    if data:
        device_state.update(data)
        device_state['lastUpdate'] = time.strftime("%H:%M:%S")
        socketio.emit('state_update', device_state)
    cmd = pending_command
    pending_command = None
    return jsonify({"cmd": cmd})

@app.route('/command', methods=['POST'])
def command():
    global pending_command
    cmd_data = request.get_json()
    if cmd_data:
        pending_command = cmd_data
        return jsonify({"status": "ok"})
    return jsonify({"status": "error"}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)