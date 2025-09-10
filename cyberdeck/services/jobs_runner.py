import os, json, time, shlex, subprocess, datetime
import sqlite3
from pathlib import Path
import numpy as np
import sounddevice as sd
import paho.mqtt.client as mqtt


DB_PATH = os.path.expanduser("~/deck/db.sqlite")
MEDIA_ROOT = Path(os.path.expanduser("~/deck/media"))


def ensure_media_dir(kind: str) -> Path:
    day = datetime.datetime.now().strftime("%Y-%m-%d")
    d = MEDIA_ROOT / ("rec" if kind == "record" else kind) / day
    d.mkdir(parents=True, exist_ok=True)
    return d


def insert_log(topic: str, payload: dict):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO logs(ts, topic, payload) VALUES(?,?,?)",
            (time.time(), topic, json.dumps(payload)),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def play_beep(duration_s: float = 0.15, freq_hz: float = 880.0, samplerate: int = 48000):
    t = np.linspace(0, duration_s, int(samplerate * duration_s), False)
    wave = 0.2 * np.sin(2 * np.pi * freq_hz * t)
    sd.play(wave.astype(np.float32), samplerate=samplerate)
    sd.wait()


def run_ffmpeg_record(seconds: int) -> str | None:
    out_dir = ensure_media_dir("record")
    ts = datetime.datetime.now().strftime("%H-%M-%S")
    out_mp4 = out_dir / f"clip_{ts}.mp4"
    # Prefer v4l2 via ffmpeg; fallback to libcamera-vid
    dev = "/dev/video0"
    if os.path.exists(dev):
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "v4l2", "-i", dev,
            "-t", str(seconds),
            "-vcodec", "libx264", "-pix_fmt", "yuv420p",
            str(out_mp4),
        ]
        try:
            subprocess.run(cmd, check=True)
            return str(out_mp4)
        except Exception:
            pass
    # Fallback: libcamera-vid (may produce h264), remux to mp4 if possible
    out_h264 = out_dir / f"clip_{ts}.h264"
    try:
        subprocess.run(["libcamera-vid", "-t", str(seconds * 1000), "-o", str(out_h264)], check=True)
        # Try remux
        try:
            subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-r", "30", "-i", str(out_h264), str(out_mp4)], check=True)
            out_h264.unlink(missing_ok=True)
            return str(out_mp4)
        except Exception:
            return str(out_h264)
    except Exception:
        return None


WHITELIST_JOBS = {
    "lan_scan": ["nmap", "-sn", "192.168.1.0/24"],
}


class Runner:
    def __init__(self):
        self.cli = mqtt.Client()
        self.cli.on_message = self.on_msg
        self.cli.connect("localhost", 1883, 60)
        self.cli.subscribe("alerts/exec")
        self.cli.subscribe("jobs/run")

    def start(self):
        self.cli.loop_forever()

    def on_msg(self, _c, _u, msg):
        try:
            d = json.loads(msg.payload)
        except Exception:
            d = {"raw": msg.payload.decode(errors='ignore')}
        topic = msg.topic
        if topic == "alerts/exec":
            self.handle_action(d)
        elif topic == "jobs/run":
            self.handle_job(d)

    def handle_action(self, d: dict):
        action = d.get("action")
        ctx = d.get("ctx", {})
        insert_log("alerts/exec", d)
        if not action:
            return
        if isinstance(action, str) and action.startswith("tone"):
            try:
                play_beep()
            except Exception:
                pass
        elif isinstance(action, str) and (action.startswith("notify") or action.startswith("push")):
            self.cli.publish("log/info", json.dumps({"msg": action, "ctx": ctx, "ts": time.time()}))
        elif action == "log":
            self.cli.publish("log/info", json.dumps({"msg": "rule matched", "ctx": ctx, "ts": time.time()}))
        elif isinstance(action, str) and action.startswith("record:"):
            try:
                seconds = int(action.split(":",1)[1])
            except Exception:
                seconds = 10
            path = run_ffmpeg_record(seconds)
            self.cli.publish("log/info", json.dumps({"msg": "recorded", "path": path, "ts": time.time()}))

    def handle_job(self, d: dict):
        name = d.get("name")
        args = d.get("args", [])
        if name in WHITELIST_JOBS:
            cmd = WHITELIST_JOBS[name]
            try:
                out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=60)
                payload = {"name": name, "ok": True, "out": out, "ts": time.time()}
            except subprocess.CalledProcessError as e:
                payload = {"name": name, "ok": False, "out": e.output, "ts": time.time()}
            except Exception as e:
                payload = {"name": name, "ok": False, "out": str(e), "ts": time.time()}
            insert_log("jobs/run", payload)
            self.cli.publish("jobs/result", json.dumps(payload))


def main():
    Runner().start()


if __name__ == "__main__":
    main()
