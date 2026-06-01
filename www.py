# 注意：monkey patch 必须放在所有导入之前！
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# ========== 存储最新传感器数据 ==========
latest_data = {
    'temperature': 25.0,
    'humidity': 50.0,
    'humanDetect': 0,
    'light': 0,
    'alarm': 0,
    'mode': 'normal'
}

# ========== 待发送给 ESP32 的控制命令 ==========
pending_command = {}

# ========== 首页 ==========
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, **latest_data)

# ========== ESP32 上报数据接口 ==========
@app.route('/update', methods=['POST'])
def update():
    global latest_data
    data = request.get_json()
    if data:
        for key in ['temperature', 'humidity', 'humanDetect', 'light', 'alarm', 'mode']:
            if key in data:
                latest_data[key] = data[key]
        # 推送给所有网页客户端
        socketio.emit('sensor_update', latest_data)

    # 返回给 ESP32 的控制命令
    cmd = pending_command.pop('cmd', None)
    if cmd is None:
        cmd = {'light': 2, 'mode': 'normal'}  # 2=自动模式
    return jsonify(cmd)

# ========== WebSocket 控制事件 ==========
@socketio.on('light_on')
def handle_light_on():
    pending_command['cmd'] = {'light': 1, 'mode': latest_data['mode']}
    latest_data['light'] = 1
    socketio.emit('sensor_update', latest_data)

@socketio.on('light_off')
def handle_light_off():
    pending_command['cmd'] = {'light': 0, 'mode': latest_data['mode']}
    latest_data['light'] = 0
    socketio.emit('sensor_update', latest_data)

@socketio.on('mode_quiet')
def handle_mode_quiet():
    pending_command['cmd'] = {'light': 2, 'mode': 'quiet'}
    latest_data['mode'] = 'quiet'
    socketio.emit('sensor_update', latest_data)

@socketio.on('mode_normal')
def handle_mode_normal():
    pending_command['cmd'] = {'light': 2, 'mode': 'normal'}
    latest_data['mode'] = 'normal'
    socketio.emit('sensor_update', latest_data)

# ========== 前端页面 ==========
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>智能家居中控</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
    <style>
        body { font-family: Arial; padding: 20px; text-align: center; }
        .data { margin: 10px; font-size: 1.2em; }
        button { margin: 8px; padding: 10px 20px; font-size: 1em; }
    </style>
</head>
<body>
    <h2>🏠 智能家居中控</h2>
    <div class="data"><b>温度：<span id="temp">--</span> ℃  |  湿度：<span id="hum">--</span> %</b></div>
    <div class="data"><b>人体：<span id="human">--</span>  |  报警：<span id="alarm">--</span></b></div>
    <div class="data"><b>LED：<span id="led">--</span>  |  模式：<span id="mode">--</span></b></div>
    <button onclick="control('light_on')">开灯</button>
    <button onclick="control('light_off')">关灯</button>
    <button onclick="control('mode_quiet')">安静模式</button>
    <button onclick="control('mode_normal')">正常模式</button>

    <script>
        var socket = io();
        socket.on('sensor_update', function(data) {
            document.getElementById('temp').innerText = data.temperature;
            document.getElementById('hum').innerText = data.humidity;
            document.getElementById('human').innerText = data.humanDetect ? '有人' : '无人';
            document.getElementById('alarm').innerText = data.alarm ? '报警中' : '正常';
            document.getElementById('led').innerText = data.light ? '开' : '关';
            document.getElementById('mode').innerText = data.mode === 'quiet' ? '安静' : '正常';
        });

        function control(action) {
            socket.emit(action);
        }
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
