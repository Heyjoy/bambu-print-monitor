# 拓竹 3D 打印监控（树莓派版）

**[English docs → README.md](README.md)**

用一台树莓派（或任意常开小主机）给拓竹 Bambu Lab 打印机做家庭监控中心：

- 📺 **实时画面** — go2rtc 拉打印机摄像头流，WebRTC 零延迟，客厅电视/手机/平板都能看
- 📊 **实时状态** — MQTT 直连打印机，进度、剩余时间、层数、喷嘴/热床温度一屏全有
- 🏠 **纯局域网** — 不走云端，不依赖拓竹 App，打印机数据不出家门
- 💰 **接近零成本** — 已有树莓派就只花电费；没有的话二手 Pi 3B+ 即可胜任

> 实测机型：**P2S**（P1/X1 系列同协议，X1 视频流路径相同）。

架构：打印机（MQTT + RTSPS）→ 树莓派（本程序 + go2rtc）→ 家里任意浏览器。

## 三步拿到凭据

全程在打印机屏幕上操作：

| 要什么 | 在哪看 |
|--------|--------|
| 打印机 IP | 设置 → 网络 |
| 序列号 SN | 设置 → 设备信息 |
| LAN 访问码 Access Code | 设置 → 网络 → 局域网模式 |

## 快速开始

```bash
git clone https://github.com/Heyjoy/bambu-print-monitor.git
cd bambu-print-monitor
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
nano .env        # 填入上面拿到的 IP / SN / 访问码

python app.py    # 浏览器打开 http://<树莓派IP>:8080
```

此时状态面板已经工作。视频画面需要再装 go2rtc（下一节）。

## 视频流：go2rtc

拓竹打印机在局域网模式下通过 RTSPS 暴露摄像头（自签名证书），[go2rtc](https://github.com/AlexxIT/go2rtc) 负责把它转成浏览器能直接播的 WebRTC。

```bash
# 1. 装 go2rtc（64 位树莓派系统选 linux_arm64，32 位选 linux_arm）
sudo wget -O /usr/local/bin/go2rtc \
  https://github.com/AlexxIT/go2rtc/releases/latest/download/go2rtc_linux_arm64
sudo chmod +x /usr/local/bin/go2rtc

# 2. 写配置（把访问码和 IP 换成你自己的）
mkdir -p ~/.config/go2rtc
cp deploy/go2rtc.yaml ~/.config/go2rtc/go2rtc.yaml
nano ~/.config/go2rtc/go2rtc.yaml

# 3. 跑起来
go2rtc
```

配置核心就一行（实测可用的写法）：

```yaml
streams:
  bambu:
    - "rtsps://bblp:<访问码>@<打印机IP>:322/streaming/live/1"
```

浏览器开 `http://<树莓派IP>:1984` 能看到 bambu 流即成功；刷新监控页，画面就出来了。

## 开机自启（systemd）

```bash
sudo cp deploy/bambu-monitor.service deploy/go2rtc.service /etc/systemd/system/
# 若代码不在 /home/pi/bambu-print-monitor，先改 service 文件里的路径
sudo systemctl daemon-reload
sudo systemctl enable --now go2rtc bambu-monitor
```

之后树莓派通电即自动恢复监控，接电视可配合浏览器 kiosk 模式全屏常显。

## 作为库使用

MQTT 核心也是一个可安装的 Python 包，方便接入 Home Assistant 或自己的自动化：

```bash
pip install "bambu-print-monitor @ git+https://github.com/Heyjoy/bambu-print-monitor"
```

```python
import bambu_monitor

bambu_monitor.start(ip='192.168.1.100', serial='你的SN', access_code='你的访问码')
# 稍等片刻后:
print(bambu_monitor.printer_status)   # dict: 状态/进度/温度/层数 ...
```

## 常见问题

**MQTT 连接失败 rc=5** — 访问码错了，或者打印机没开局域网模式。重新对一遍屏幕上的 Access Code（注意打印机重置局域网模式后访问码会变）。

**状态有了但视频黑屏** — 先开 `http://<树莓派IP>:1984` 确认 go2rtc 自己能播；不能播就是 go2rtc.yaml 里的访问码/IP 不对。能播但监控页不行，检查 `.env` 里 `GO2RTC_URL` 是否指对了地址。

**过一会状态卡住不动** — P1/P2 系列不会主动推全量状态，本程序每 10 秒发一次 `pushall` 请求；若打印机固件升级后行为变化，欢迎提 issue。

**接口速查** — `GET /api/status` 返回全部状态 JSON。

## 项目结构

```
bambu_monitor/           # 可 pip 安装的包（可复用核心）
  mqtt_client.py         #   打印机 MQTT 长连接、状态字典
  formatters.py          #   展示格式化纯函数
app.py                   # Flask 入口：监控页 + /api/status
config.py                # 监控页的 .env 配置加载
templates/monitor.html   # 监控页（深色、响应式、可全屏）
deploy/                  # go2rtc 配置示例 + systemd 服务文件
```

## 关于

这是我家里跑了很久的真实配置的开源精简版。更多 3D 打印、树莓派、家庭自动化的实践分享，欢迎关注公众号，也欢迎 star / issue 交流。

MIT License
