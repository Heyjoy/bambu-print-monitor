"""配置与凭据 — 全部来自环境变量 / .env 文件，绝不硬编码入库。

复制 .env.example 为 .env 并填入你自己的打印机信息。
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env')

# 打印机连接（必填项缺失时启动即报错，比静默连不上好排查）
PRINTER_IP = os.environ.get('PRINTER_IP')
PRINTER_PORT = int(os.environ.get('PRINTER_PORT', '8883'))
SERIAL_NUMBER = os.environ.get('PRINTER_SERIAL')
ACCESS_CODE = os.environ.get('PRINTER_ACCESS_CODE')

# go2rtc 视频流（默认与本服务同机运行）
GO2RTC_URL = os.environ.get('GO2RTC_URL', 'http://127.0.0.1:1984')
STREAM_NAME = os.environ.get('STREAM_NAME', 'bambu')

# Web 服务端口
PORT = int(os.environ.get('PORT', '8080'))

_missing = [k for k, v in {
    'PRINTER_IP': PRINTER_IP,
    'PRINTER_SERIAL': SERIAL_NUMBER,
    'PRINTER_ACCESS_CODE': ACCESS_CODE,
}.items() if not v]
if _missing:
    sys.exit(
        f'缺少必填配置: {", ".join(_missing)}\n'
        '请复制 .env.example 为 .env 并填入你的打印机信息（见 README「三步拿到凭据」）。'
    )
