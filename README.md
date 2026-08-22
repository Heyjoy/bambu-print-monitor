# Bambu Print Monitor

**[中文文档 → README.zh-CN.md](README.zh-CN.md)**

Turn a Raspberry Pi (or any always-on box) into a home monitoring center for your Bambu Lab 3D printer:

- 📺 **Live camera** — go2rtc pulls the printer's camera stream and serves it as zero-latency WebRTC, viewable on your TV, phone, or tablet
- 📊 **Live status** — direct MQTT connection to the printer: progress, remaining time, layers, nozzle/bed temperatures on one page
- 🏠 **LAN only** — no cloud, no Bambu app dependency; printer data never leaves your home
- 💰 **Near-zero cost** — just electricity if you already own a Pi; a used Pi 3B+ is plenty

> Tested on a **P2S**. P1/X1 series use the same protocol (X1 shares the same video stream path).

Architecture: printer (MQTT + RTSPS) → Raspberry Pi (this app + go2rtc) → any browser in your home.

## Get your credentials (all on the printer screen)

| What | Where |
|------|-------|
| Printer IP | Settings → Network |
| Serial number (SN) | Settings → Device info |
| LAN Access Code | Settings → Network → LAN Mode |

## Quick start

```bash
git clone https://github.com/Heyjoy/bambu-print-monitor.git
cd bambu-print-monitor
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
nano .env        # fill in the IP / SN / Access Code from above

python app.py    # open http://<pi-ip>:8080 in a browser
```

The status panel works at this point. For the camera view, install go2rtc (next section).

## Camera stream: go2rtc

In LAN mode the printer exposes its camera over RTSPS (self-signed certificate). [go2rtc](https://github.com/AlexxIT/go2rtc) converts it to browser-playable WebRTC.

```bash
# 1. Install go2rtc (linux_arm64 for 64-bit Pi OS, linux_arm for 32-bit)
sudo wget -O /usr/local/bin/go2rtc \
  https://github.com/AlexxIT/go2rtc/releases/latest/download/go2rtc_linux_arm64
sudo chmod +x /usr/local/bin/go2rtc

# 2. Write the config (use your own access code and IP)
mkdir -p ~/.config/go2rtc
cp deploy/go2rtc.yaml ~/.config/go2rtc/go2rtc.yaml
nano ~/.config/go2rtc/go2rtc.yaml

# 3. Run it
go2rtc
```

The config boils down to one line (verified working):

```yaml
streams:
  bambu:
    - "rtsps://bblp:<access-code>@<printer-ip>:322/streaming/live/1"
```

Open `http://<pi-ip>:1984` — if the `bambu` stream plays there, refresh the monitor page and the video appears.

## Start on boot (systemd)

```bash
sudo cp deploy/bambu-monitor.service deploy/go2rtc.service /etc/systemd/system/
# adjust paths in the service files if the code is not in /home/pi/bambu-print-monitor
sudo systemctl daemon-reload
sudo systemctl enable --now go2rtc bambu-monitor
```

After this the Pi resumes monitoring on every power-up; pair it with a TV and a browser in kiosk mode for an always-on wall display.

## Use as a library

The MQTT core is also an installable package, handy for Home Assistant bridges or your own automation:

```bash
pip install "bambu-print-monitor @ git+https://github.com/Heyjoy/bambu-print-monitor"
```

```python
import bambu_monitor

bambu_monitor.start(ip='192.168.1.100', serial='YOUR_SN', access_code='YOUR_CODE')
# ... a moment later:
print(bambu_monitor.printer_status)   # dict: state / progress / temps / layers ...
```

## FAQ

**MQTT fails with rc=5** — wrong Access Code, or LAN mode is disabled on the printer. Re-check the code on the printer screen (it changes whenever LAN mode is reset).

**Status works but video is black** — first open `http://<pi-ip>:1984` and confirm go2rtc itself can play the stream; if not, the access code/IP in go2rtc.yaml is wrong. If go2rtc plays but the monitor page doesn't, check `GO2RTC_URL` in `.env`.

**Status freezes after a while** — P1/P2 printers never push full state unsolicited; this app requests `pushall` every 10 s. If a firmware update changes this behavior, please open an issue.

**API** — `GET /api/status` returns the full status JSON.

> Note: the dashboard UI labels are currently Chinese. PRs for i18n are welcome.

## Project layout

```
bambu_monitor/           # installable package (the reusable core)
  mqtt_client.py         #   printer MQTT connection, status dict
  formatters.py          #   display formatting helpers
app.py                   # Flask dashboard: monitor page + /api/status
config.py                # .env loading for the dashboard
templates/monitor.html   # dashboard page (dark, responsive, fullscreen)
deploy/                  # go2rtc config example + systemd units
```

## About

This is the open-source distilled version of a setup that has been running in my home for a long time. Star / issue / PR welcome.

MIT License
