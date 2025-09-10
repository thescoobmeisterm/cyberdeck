import json, time, os, sqlite3, io
import paho.mqtt.client as mqtt
import numpy as np
import cv2


# Placeholder: integrate 'face_recognition' or a tiny insightface later
DB_PATH = os.environ.get("DECK_DB_PATH", os.path.expanduser("~/deck/db.sqlite"))


def _npy_to_bytes(arr: np.ndarray) -> bytes:
    buf = io.BytesIO()
    np.save(buf, arr.astype(np.float32))
    return buf.getvalue()


def _bytes_to_npy(data: bytes) -> np.ndarray:
    return np.load(io.BytesIO(data))


def _load_image(path: str) -> np.ndarray | None:
    try:
        img = cv2.imread(path)
        return img
    except Exception:
        return None


def _detect_face_bgr(img_bgr: np.ndarray) -> np.ndarray | None:
    try:
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(60, 60))
        if len(faces) == 0:
            return None
        # pick largest
        x, y, w, h = max(faces, key=lambda r: r[2] * r[3])
        face = img_bgr[y:y+h, x:x+w]
        return face
    except Exception:
        return None


def _embed_face(img_bgr: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (96, 96), interpolation=cv2.INTER_AREA)
    # intensity histogram
    hist = cv2.calcHist([resized], [0], None, [32], [0, 256]).flatten()
    hist = hist / (np.linalg.norm(hist) + 1e-8)
    # gradient magnitude histogram
    gx = cv2.Sobel(resized, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(resized, cv2.CV_32F, 0, 1, ksize=3)
    mag = cv2.magnitude(gx, gy)
    ghist = cv2.calcHist([mag.astype(np.uint8)], [0], None, [32], [0, 256]).flatten()
    ghist = ghist / (np.linalg.norm(ghist) + 1e-8)
    emb = np.concatenate([hist, ghist]).astype(np.float32)
    return emb


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) + 1e-8) * (np.linalg.norm(b) + 1e-8)
    return float(np.dot(a, b) / denom)


def ensure_faces_table():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("CREATE TABLE IF NOT EXISTS faces (id INTEGER PRIMARY KEY, name TEXT NOT NULL, embedding BLOB NOT NULL, added_ts REAL NOT NULL)")
        conn.commit(); conn.close()
    except Exception:
        pass


def main():
    ensure_faces_table()
    cli = mqtt.Client(); cli.connect("localhost",1883,60); cli.loop_start()

    pending = {"mode": None, "name": None}

    def on_msg(_c,_u,msg):
        topic = msg.topic
        if topic == "face/enroll":
            # Direct enroll from latest snapshot path provided
            try:
                d = json.loads(msg.payload)
                name = d.get("name","?")
                path = d.get("path")
                if not path:
                    cli.publish("face/enroll_result", json.dumps({"ok": False, "error": "missing path"}))
                    return
                img = _load_image(path)
                face = _detect_face_bgr(img) if img is not None else None
                if face is None:
                    cli.publish("face/enroll_result", json.dumps({"ok": False, "error": "no face"}))
                    return
                emb = _embed_face(face)
                conn = sqlite3.connect(DB_PATH)
                conn.execute("INSERT INTO faces(name, embedding, added_ts) VALUES(?,?,?)", (name, _npy_to_bytes(emb), time.time()))
                conn.commit(); conn.close()
                cli.publish("face/enroll_result", json.dumps({"ok": True, "name": name}))
            except Exception as e:
                cli.publish("face/enroll_result", json.dumps({"ok": False, "error": str(e)}))
        elif topic == "face/list":
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor(); cur.execute("SELECT id, name, LENGTH(embedding), added_ts FROM faces ORDER BY added_ts DESC LIMIT 100")
                rows = cur.fetchall(); conn.close()
                cli.publish("face/list_result", json.dumps({"ok": True, "rows": rows}))
            except Exception as e:
                cli.publish("face/list_result", json.dumps({"ok": False, "error": str(e)}))
        elif topic == "face/recognize":
            # Trigger snapshot and wait for cam/snap_ok
            pending["mode"] = "recognize"; pending["name"] = None
            cli.publish("cam/snap", json.dumps({}))
        elif topic == "face/enroll_request":
            try:
                d = json.loads(msg.payload)
                pending["mode"] = "enroll"; pending["name"] = d.get("name","?")
                cli.publish("cam/snap", json.dumps({}))
            except Exception:
                pass
        elif topic == "cam/snap_ok":
            try:
                if pending["mode"] is None:
                    return
                d = json.loads(msg.payload)
                path = d.get("path")
                img = _load_image(path)
                face = _detect_face_bgr(img) if img is not None else None
                if face is None:
                    if pending["mode"] == "enroll":
                        cli.publish("face/enroll_result", json.dumps({"ok": False, "error": "no face"}))
                    else:
                        cli.publish("face/recognize_result", json.dumps({"ok": False, "error": "no face"}))
                    pending["mode"] = None; pending["name"] = None
                    return
                emb = _embed_face(face)
                if pending["mode"] == "enroll":
                    name = pending["name"] or "?"
                    conn = sqlite3.connect(DB_PATH)
                    conn.execute("INSERT INTO faces(name, embedding, added_ts) VALUES(?,?,?)", (name, _npy_to_bytes(emb), time.time()))
                    conn.commit(); conn.close()
                    cli.publish("face/enroll_result", json.dumps({"ok": True, "name": name}))
                else:
                    # recognize
                    conn = sqlite3.connect(DB_PATH)
                    cur = conn.cursor(); cur.execute("SELECT name, embedding FROM faces")
                    rows = cur.fetchall(); conn.close()
                    best_name = None; best_sim = 0.0
                    for name, blob in rows:
                        try:
                            db_emb = _bytes_to_npy(blob)
                            sim = _cosine_similarity(emb, db_emb)
                            if sim > best_sim:
                                best_sim = sim; best_name = name
                        except Exception:
                            continue
                    ok = best_name is not None and best_sim >= 0.85
                    if ok:
                        cli.publish("cam/face", json.dumps({"event":"face","name": best_name, "conf": round(float(best_sim),2), "ts": time.time()}))
                    cli.publish("face/recognize_result", json.dumps({"ok": ok, "name": best_name, "conf": best_sim}))
                pending["mode"] = None; pending["name"] = None
            except Exception as e:
                pending["mode"] = None; pending["name"] = None
                cli.publish("face/recognize_result", json.dumps({"ok": False, "error": str(e)}))

    cli.on_message = on_msg
    cli.subscribe("face/enroll")
    cli.subscribe("face/list")
    cli.subscribe("face/recognize")
    cli.subscribe("face/enroll_request")
    cli.subscribe("cam/snap_ok")
    while True:
        time.sleep(0.1)


if __name__ == "__main__":
    main()
