import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO, emit
import json
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

latest_data = {
    "temperature": "--",
    "humidity": "--"
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>智能家居监控</title>
<style>
  body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
  .container { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 20px; padding: 40px; box-shadow: 0 8px 32px rgba(0,0,0,0.3); text-align: center; max-width: 400px; width: 90%; }
  h1 { margin-bottom: 30px; font-size: 2.5rem; font-weight: 300; }
  .card { background: rgba(255,255,255,0.15); border-radius: 15px; padding: 25px; margin: 15px 0; transition: transform 0.3s; }
  .card:hover { transform: scale(1.02); }
  .label { font-size: 1.2rem; opacity: 0.8; margin-bottom: 10px; }
  .value { font-size: 3rem; font-weight: 700; }
  .unit { font-size: 1.5rem; opacity: 0.7; }
  .status { margin-top: 20px; font-size: 0.9rem; opacity: 0.6; }
  @media (max-width: 480px) { h1 { font-size: 2rem; } .value { font-size: 2.5rem; } }
</style>
</head>
<body>
<div class="container">
  <h1>🏠 智能家居</h1>
  <div class="card">
    <div class="label">🌡️ 温度</div>
    <div class="value"><span id="temp">{{ temperature }}</span> <span class="unit">℃</span></div>
  </div>
  <div class="card">
    <div class="label">💧 湿度</div>
    <div class="value"><span id="hum">{{ humidity }}</span> <span class="unit">%</span></div>
  </div>
  <div class="status" id="status">等待数据更新...</div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.4/socket.io.min.js"></script>
<script>
  const socket = io();
  const tempEl = document.getElementById('temp');
  const humEl = document.getElementById('hum');
  const statusEl = document.getElementById('status');

  socket.on('update', (data) => {
    tempEl.textContent = data.temperature;
    humEl.textContent = data.humidity;
    const now = new Date().toLocaleTimeString();
    statusEl.textContent = `✅ 最后更新: ${now}`;
  });
</script>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, **latest_data)

@app.route('/update', methods=['POST'])
def update():
    global latest_data
    data = request.get_json()
    if data:
        latest_data = {
            "temperature": data.get('temperature', '--'),
            "humidity": data.get('humidity', '--')
        }
        socketio.emit('update', latest_data, broadcast=True)
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
