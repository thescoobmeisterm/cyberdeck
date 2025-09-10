#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update
sudo apt-get install -y python3-full python3-pip python3-opencv ffmpeg \
  mosquitto libatlas-base-dev libportaudio2 libsndfile1 \
  nmap tcpdump sqlite3

python3 -m pip install -U pip
pip3 install -r requirements.txt

mkdir -p ~/deck/media ~/deck/state db
sqlite3 ~/deck/db.sqlite < db/schema.sql

echo "Done. Enable services per README."
