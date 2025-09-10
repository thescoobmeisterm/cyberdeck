#!/usr/bin/env bash
set -euo pipefail

repo_dir=$(cd "$(dirname "$0")/.." && pwd)

echo "Deploying from $repo_dir"

if ! command -v mosquitto >/dev/null 2>&1; then
  sudo apt-get update && sudo apt-get install -y mosquitto
fi
sudo systemctl enable mosquitto --now

# App unit
sudo ln -sf "$repo_dir/packaging/systemd/cyberdeck-app.service" /etc/systemd/system/
sudo systemctl enable cyberdeck-app

services=(sys_health audio_meter motion_cam net_mgr jobs_runner)
for s in "${services[@]}"; do
  sudo ln -sf "$repo_dir/packaging/systemd/cyberdeck-@.service" \
    "/etc/systemd/system/cyberdeck-$s.service"
  sudo systemctl enable "cyberdeck-$s"
done

echo "Reloading systemd and starting units..."
sudo systemctl daemon-reload
sudo systemctl start cyberdeck-app || true
for s in "${services[@]}"; do
  sudo systemctl start "cyberdeck-$s" || true
done

echo "Done."
