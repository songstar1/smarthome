from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO, emit
import eventlet
eventlet.monkey_patch()
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
# ========== 模拟数据（ESP32 未连接时显示） ==========
latest_data = {
    'temperature': 25.0,
    'humidity': 50.0,
    'humanDetect': 0,
    'light': 0,
    'alarm': 0,
    'mode': 'normal'
}
# 给 ESP32 的控制命令（此处可扩展）
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
        # 更新数据，只保留我们需要的字段
        for key in ['temperature', 'humidity', 'humanDetect', 'light', 'alarm', 'mode']:
            if key in data:
                latest_data[key] = data[key]
        # 推送给所有网页客户端
        socketio.emit('sensor_update', latest_data)
    # 返回给 ESP32 的控制命令（如果有待发的命令则发送，否则默认发自动模式）
    cmd = pending_command.pop('cmd', None)
    if cmd is None:
        cmd = {'light': 2, 'mode': 'normal'}  # 2=自动模式
    return jsonify(cmd)
# ========== 网页按钮事件（通过 WebSocket） ==========
@socketio.on('light_on')
def handle_light_on():
    global pending_command
    pending_command['cmd'] = {'light': 1, 'mode': latest_data['mode']}
    # 立即更新本地显示（实际状态等 ESP32 下次上报会再次更新）
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
