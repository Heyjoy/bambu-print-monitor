"""bambu_monitor — LAN-only status monitoring for Bambu Lab 3D printers.

Usage:
    import bambu_monitor
    bambu_monitor.start(ip='192.168.1.100', serial='XXXX', access_code='XXXX')
    print(bambu_monitor.printer_status)
"""
from bambu_monitor.mqtt_client import (
    printer_status,
    start,
    is_stale,
    is_printer_reachable,
)
from bambu_monitor import formatters

__version__ = '1.1.0'
__all__ = ['printer_status', 'start', 'is_stale', 'is_printer_reachable', 'formatters']
