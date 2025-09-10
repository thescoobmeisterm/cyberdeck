#!/usr/bin/env bash
set -euo pipefail

# Resolve repository root (this script is at <repo>/scripts/install.sh)
repo_dir=$(cd "$(dirname "$0")/.." && pwd)

sudo apt-get update
sudo apt-get install -y \
  python3-full python3-pip python3-venv \
  python3-opencv ffmpeg mosquitto sqlite3 \
  mosquitto-clients iw alsa-utils \
  wireless-tools \
  libatlas-base-dev libportaudio2 libsndfile1 \
  libsdl2-2.0-0 libsdl2-image-2.0-0 libsdl2-mixer-2.0-0 libsdl2-ttf-2.0-0 \
  libgl1 libgles2 gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
  nmap tcpdump network-manager

# Create venv that can see apt-installed site packages (e.g., cv2)
if [ ! -d "$repo_dir/.venv" ]; then
  python3 -m venv "$repo_dir/.venv" --system-site-packages
fi
source "$repo_dir/.venv/bin/activate"
python -m pip install -U pip setuptools wheel
pip install -r "$repo_dir/requirements.txt"

mkdir -p ~/deck/media ~/deck/state "$repo_dir/db"
sqlite3 ~/deck/db.sqlite < "$repo_dir/db/schema.sql"

echo "Done. Enable services per README or run $repo_dir/scripts/deploy.sh."
