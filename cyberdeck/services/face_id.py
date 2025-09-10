import json, time, os, sqlite3
import paho.mqtt.client as mqtt


# Placeholder: integrate 'face_recognition' or a tiny insightface later
DB_PATH = os.environ.get("DECK_DB_PATH", os.path.expanduser("~/deck/db.sqlite"))


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

    def on_msg(_c,_u,msg):
        if msg.topic == "face/enroll":
            try:
                d = json.loads(msg.payload)
                name = d.get("name","?")
                # For now, store provided embedding bytes if any; fuller pipeline later
                emb_b64 = d.get("embedding_b64")
                emb = emb_b64.encode() if isinstance(emb_b64, str) else b""
                conn = sqlite3.connect(DB_PATH)
                conn.execute("INSERT INTO faces(name, embedding, added_ts) VALUES(?,?,?)", (name, emb, time.time()))
                conn.commit(); conn.close()
                cli.publish("face/enroll_result", json.dumps({"ok": True, "name": name}))
            except Exception as e:
                cli.publish("face/enroll_result", json.dumps({"ok": False, "error": str(e)}))
        elif msg.topic == "face/list":
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor(); cur.execute("SELECT id, name, LENGTH(embedding), added_ts FROM faces ORDER BY added_ts DESC LIMIT 100")
                rows = cur.fetchall(); conn.close()
                cli.publish("face/list_result", json.dumps({"ok": True, "rows": rows}))
            except Exception as e:
                cli.publish("face/list_result", json.dumps({"ok": False, "error": str(e)}))

    cli.on_message = on_msg
    cli.subscribe("face/enroll")
    cli.subscribe("face/list")
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
