run:
	PYTHONPATH=. python3 app/main.py

lint:
	rufflehog --exclude .git || true

dev-mqtt:
	sudo systemctl start mosquitto

seed:
	python3 scripts/create_db.py

services:
	sudo systemctl restart cyberdeck-sys_health cyberdeck-audio_meter cyberdeck-motion_cam || true
