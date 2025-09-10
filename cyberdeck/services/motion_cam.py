import cv2, time, json, os, yaml
from collections import deque
from pathlib import Path
import paho.mqtt.client as mqtt


def load_settings():
    cfg_path = os.environ.get("DECK_CONFIG_PATH") or os.path.expanduser("config/deck.yaml")
    try:
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f) or {}
    except Exception:
        cfg = {}
    cam = cfg.get("camera", {})
    motion = (cam or {}).get("motion", {})
    rec = (cam or {}).get("record", {})
    device = cam.get("device", 0)
    res = cam.get("res", [1280, 720])
    fps = cam.get("fps", 30)
    sensitivity = motion.get("sensitivity", 0.6)
    min_area = motion.get("min_area", 800)
    preroll_s = rec.get("preroll_s", 5)
    postroll_s = rec.get("postroll_s", 10)
    return device, int(res[0]), int(res[1]), int(fps), float(sensitivity), int(min_area), int(preroll_s), int(postroll_s)


def main(device=0, width=1280, height=720, fps=30, sensitivity=0.6, min_area=800,
         preroll_s: int = 5, postroll_s: int = 10):
    # Override defaults from YAML if available
    device, width, height, fps, sensitivity, min_area, preroll_s, postroll_s = load_settings()
    cli = mqtt.Client(); cli.connect("localhost",1883,60); cli.loop_start()
    privacy_on = False
    last_frame = None
    snap_request = False
    def on_msg(_c,_u,msg):
        nonlocal privacy_on
        nonlocal snap_request
        if msg.topic == "privacy/state":
            try:
                d = json.loads(msg.payload)
                privacy_on = bool(d.get("on"))
            except Exception:
                privacy_on = False
        elif msg.topic == "cam/snap":
            snap_request = True
    cli.on_message = on_msg
    cli.subscribe("privacy/state")
    cli.subscribe("cam/snap")
    cap = cv2.VideoCapture(device)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, fps)
    mog = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=16, detectShadows=False)
    # Circular buffer of recent frames for pre-roll
    maxlen = max(1, int(preroll_s * fps))
    ring = deque(maxlen=maxlen)
    last_trigger_ts = 0.0
    recording_until = 0.0
    record_frames = []
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    media_root = Path(os.path.expanduser("~/deck/media"))
    (media_root / "rec").mkdir(parents=True, exist_ok=True)
    (media_root / "snap").mkdir(parents=True, exist_ok=True)

    while True:
        ok, frame = cap.read()
        if not ok: time.sleep(0.1); continue
        last_frame = frame
        fg = mog.apply(frame)
        cnts, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        area = max((cv2.contourArea(c) for c in cnts), default=0)
        score = min(1.0, area / (width*height/20.0))
        # push frame into ring always
        ring.append(frame.copy())

        now = time.time()
        if not privacy_on and area > min_area and score >= sensitivity:
            payload = {"event":"motion","score": float(score), "ts": now}
            cli.publish("cam/motion", json.dumps(payload))
            last_trigger_ts = now
            # If not already recording, start collection with preroll
            if recording_until < now:
                # snapshot
                snap_path = media_root / "snap" / f"snap_{int(now)}.jpg"
                cv2.imwrite(str(snap_path), frame)
                # start new recording window
                recording_until = now + postroll_s
                record_frames = list(ring)  # include pre-roll frames
        # If in recording window, keep collecting frames
        if recording_until >= now:
            record_frames.append(frame.copy())
        # Handle snapshot request
        if snap_request and last_frame is not None:
            snap_request = False
            day_dir = media_root / "snap"
            day_dir.mkdir(parents=True, exist_ok=True)
            snap_path = day_dir / f"snap_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(str(snap_path), last_frame)
            cli.publish("cam/snap_ok", json.dumps({"path": str(snap_path), "ts": time.time()}))

        # If window elapsed and we have frames, write to file
        if recording_until < now and record_frames:
            day_dir = media_root / "rec" / time.strftime("%Y-%m-%d")
            day_dir.mkdir(parents=True, exist_ok=True)
            fname = day_dir / f"clip_{time.strftime('%H-%M-%S')}.mp4"
            writer = cv2.VideoWriter(str(fname), fourcc, fps, (width, height))
            for f in record_frames:
                writer.write(f)
            writer.release()
            cli.publish("cam/recorded", json.dumps({"path": str(fname), "frames": len(record_frames), "ts": time.time()}))
            record_frames = []


if __name__ == "__main__":
    main()
