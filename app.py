#!/usr/bin/env python3
"""拓竹 3D 打印监控 — 状态采集 + 实时画面的家庭监控页。
Bambu Lab home print monitor — live status + camera dashboard.

树莓派 / 任意常开小主机上运行 (run on a Raspberry Pi or any always-on box):
    python app.py
浏览器打开 http://<主机IP>:8080 即可。
"""
from flask import Flask, jsonify, render_template

from bambu_monitor import mqtt_client
from bambu_monitor.formatters import format_remaining_time, state_cn
from config import (
    ACCESS_CODE, GO2RTC_URL, PORT, PRINTER_IP, PRINTER_PORT,
    SERIAL_NUMBER, STREAM_NAME,
)

app = Flask(__name__)


@app.route('/')
def monitor():
    return render_template(
        'monitor.html',
        go2rtc_url=GO2RTC_URL,
        stream_name=STREAM_NAME,
    )


@app.route('/api/status')
def api_status():
    s = mqtt_client.printer_status
    online = s['online']
    if mqtt_client.is_stale():
        online = mqtt_client.is_printer_reachable()
        s['online'] = online
    return jsonify({
        'online': online,
        'state': s['state'],
        'state_cn': state_cn(s['state']),
        'progress': s['progress'],
        'remaining_time': format_remaining_time(s['remaining_time']),
        'nozzle_temp': s['nozzle_temp'],
        'nozzle_target': s['nozzle_target'],
        'bed_temp': s['bed_temp'],
        'bed_target': s['bed_target'],
        'layer_num': s['layer_num'],
        'total_layers': s['total_layers'],
        'file_name': s['file_name'],
    })


mqtt_client.start(PRINTER_IP, SERIAL_NUMBER, ACCESS_CODE, PRINTER_PORT)

if __name__ == '__main__':
    print('🖨️  bambu-print-monitor 启动中...')
    print(f'📺 访问 http://0.0.0.0:{PORT}')
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
