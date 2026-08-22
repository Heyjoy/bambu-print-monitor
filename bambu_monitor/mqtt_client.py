"""Persistent MQTT connection to a Bambu Lab printer (LAN mode).

The printer runs TLS MQTT on port 8883 with a self-signed certificate.
Username is always ``bblp``; the password is the LAN Access Code shown
on the printer screen. Works with P1 / P2 / X1 series.
"""
import json
import platform
import ssl
import subprocess
import sys
import threading
import time

import paho.mqtt.client as mqtt

STALE_AFTER_SECONDS = 30
POLL_INTERVAL_SECONDS = 10

printer_status = {
    'online': False,
    'state': 'unknown',
    'progress': 0,
    'remaining_time': 0,
    'nozzle_temp': 0,
    'nozzle_target': 0,
    'bed_temp': 0,
    'bed_target': 0,
    'layer_num': 0,
    'total_layers': 0,
    'file_name': '',
    'last_update': 0,
}

# report payload field -> printer_status key
_FIELD_MAP = {
    'gcode_state': 'state',
    'mc_percent': 'progress',
    'mc_remaining_time': 'remaining_time',
    'nozzle_temper': 'nozzle_temp',
    'nozzle_target_temper': 'nozzle_target',
    'bed_temper': 'bed_temp',
    'bed_target_temper': 'bed_target',
    'layer_num': 'layer_num',
    'total_layer_num': 'total_layers',
}

_client = None
_ip = None
_port = 8883
_serial = None
_access_code = None


def log(msg):
    print(msg, flush=True)
    sys.stdout.flush()


def is_stale() -> bool:
    """True when no MQTT report has arrived recently."""
    return time.time() - printer_status['last_update'] > STALE_AFTER_SECONDS


def is_printer_reachable() -> bool:
    """Ping fallback used when MQTT data is stale."""
    if not _ip:
        return False
    if platform.system() == 'Windows':
        cmd = ['ping', '-n', '1', '-w', '1000', _ip]
    else:
        cmd = ['ping', '-c', '1', '-W', '1', _ip]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=3)
        return r.returncode == 0
    except Exception:
        return False


def _on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        log('MQTT connected')
        printer_status['online'] = True
        client.subscribe(f'device/{_serial}/report')
        # P1/P2 series never push full state unsolicited; request it.
        client.publish(f'device/{_serial}/request',
                       json.dumps({'pushing': {'command': 'pushall'}}))
    else:
        log(f'MQTT connect failed: rc={rc} (rc=5 usually means wrong Access Code)')
        printer_status['online'] = False


def _on_disconnect(client, userdata, rc, properties=None, reasoncode=None):
    printer_status['online'] = False


def _on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        p = data.get('print')
        if not p:
            return
        printer_status['last_update'] = time.time()
        printer_status['online'] = True
        for src, dst in _FIELD_MAP.items():
            if src in p:
                printer_status[dst] = p[src]
        if 'gcode_file' in p:
            f = p['gcode_file']
            printer_status['file_name'] = f.split('/')[-1] if f else ''
    except Exception as e:
        log(f'MQTT message parse error: {e}')


def _poll_loop():
    while True:
        time.sleep(POLL_INTERVAL_SECONDS)
        if _client and _client.is_connected():
            try:
                _client.publish(f'device/{_serial}/request',
                                json.dumps({'pushing': {'command': 'pushall'}}))
            except Exception as e:
                log(f'pushall request failed: {e}')


def _connect_loop():
    global _client
    _client = mqtt.Client(
        client_id=f'bambu_monitor_{int(time.time())}',
        protocol=mqtt.MQTTv311,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    )
    _client.username_pw_set('bblp', _access_code)
    _client.on_connect = _on_connect
    _client.on_disconnect = _on_disconnect
    _client.on_message = _on_message
    # The printer uses a self-signed certificate; LAN use only.
    _client.tls_set(cert_reqs=ssl.CERT_NONE)
    _client.tls_insecure_set(True)

    while True:
        try:
            log(f'connecting MQTT: {_ip}:{_port}')
            _client.connect(_ip, _port, 60)
            _client.loop_forever()
        except Exception as e:
            log(f'MQTT connect failed: {e}')
            printer_status['online'] = False
            time.sleep(5)


def start(ip: str, serial: str, access_code: str, port: int = 8883) -> None:
    """Start the MQTT connection and poll loop (two daemon threads)."""
    global _ip, _port, _serial, _access_code
    if not (ip and serial and access_code):
        raise ValueError('ip, serial and access_code are all required')
    _ip, _port, _serial, _access_code = ip, port, serial, access_code
    threading.Thread(target=_connect_loop, daemon=True).start()
    threading.Thread(target=_poll_loop, daemon=True).start()
