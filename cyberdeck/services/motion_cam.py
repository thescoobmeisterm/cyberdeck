import cv2, time, json, paho.mqtt.client as mqtt


def main(device=0, width=1280, height=720, fps=30, sensitivity=0.6, min_area=800):
    cli = mqtt.Client(); cli.connect("localhost",1883,60); cli.loop_start()
    cap = cv2.VideoCapture(device)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, fps)
    mog = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=16, detectShadows=False)

    while True:
        ok, frame = cap.read()
        if not ok: time.sleep(0.1); continue
        fg = mog.apply(frame)
        cnts, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        area = max((cv2.contourArea(c) for c in cnts), default=0)
        score = min(1.0, area / (width*height/20.0))
        if area > min_area and score >= sensitivity:
            payload = {"event":"motion","score": float(score), "ts": time.time()}
            cli.publish("cam/motion", json.dumps(payload))


if __name__ == "__main__":
    main()
