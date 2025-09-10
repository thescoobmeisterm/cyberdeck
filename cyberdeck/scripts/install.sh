#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update
sudo apt-get install -y \
  python3-full python3-pip python3-venv \
  python3-opencv ffmpeg mosquitto sqlite3 \
  libatlas-base-dev libportaudio2 libsndfile1 \
  libsdl2-2.0-0 libsdl2-image-2.0-0 libsdl2-mixer-2.0-0 libsdl2-ttf-2.0-0 \
  libgl1 libgles2 gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
  nmap tcpdump

# Create venv that can see apt-installed site packages (e.g., cv2)
if [ ! -d .venv ]; then
  python3 -m venv .venv --system-site-packages
fi
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
pip install -r requirements.txt

mkdir -p ~/deck/media ~/deck/state db
sqlite3 ~/deck/db.sqlite < db/schema.sql

echo "Done. Enable services per README or run scripts/deploy.sh."
