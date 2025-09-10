# Cyberdeck GUI (Pi-5 + 5" Touch)

Touch-first dashboard with modular widgets and MQTT-backed services.

## Quick Start

1. Install deps and setup DB

```bash
bash scripts/install.sh
```

2. Run UI in dev

```bash
make run
```

3. Enable services (systemd)

```bash
sudo apt-get install -y mosquitto
sudo systemctl enable mosquitto --now
sudo ln -s /home/pi/cyberdeck/packaging/systemd/cyberdeck-app.service /etc/systemd/system/
sudo systemctl enable cyberdeck-app
sudo systemctl start cyberdeck-app

for s in sys_health audio_meter motion_cam; do
  sudo ln -s /home/pi/cyberdeck/packaging/systemd/cyberdeck-@.service /etc/systemd/system/cyberdeck-$s.service
  sudo systemctl enable cyberdeck-$s
  sudo systemctl start cyberdeck-$s
done
```

## Layout
See `config/deck.yaml` and `db/schema.sql`.

## Notes
- MQTT: localhost only
- Camera via OpenCV (libcamera v4l2 bridge)
- Audio via sounddevice