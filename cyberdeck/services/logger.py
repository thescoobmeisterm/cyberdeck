import os, json, time, sqlite3
import paho.mqtt.client as mqtt


DB_PATH = os.environ.get("DECK_DB_PATH", os.path.expanduser("~/deck/db.sqlite"))


def ensure_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, ts REAL NOT NULL, topic TEXT NOT NULL, payload TEXT NOT NULL)")
    conn.commit()
    conn.close()


def main():
    ensure_db()
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = conn.cursor()
    cli = mqtt.Client()
    cli.connect("localhost", 1883, 60)

    def on_msg(_c,_u,msg):
        try:
            # Store raw JSON or bytes decoded best-effort
            payload = msg.payload.decode(errors='ignore') if isinstance(msg.payload, (bytes, bytearray)) else str(msg.payload)
            cur.execute("INSERT INTO logs(ts, topic, payload) VALUES(?,?,?)", (time.time(), msg.topic, payload))
            conn.commit()
        except Exception:
            pass

    cli.on_message = on_msg
    cli.subscribe("#")
    cli.loop_forever()


if __name__ == "__main__":
    main()
