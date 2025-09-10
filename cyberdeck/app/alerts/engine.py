import ast, time, json, os, sqlite3
from .rules import compile_rules


class AlertEngine:
    def __init__(self, bus, cfg):
        self.bus = bus
        self.rules = compile_rules(cfg.get("rules", []))
        self.bus.sub("#", self._eval)
        # Prepare DB for alert inserts
        self._db_path = os.environ.get("DECK_DB_PATH") or os.path.expanduser("~/deck/db.sqlite")
        try:
            conn = sqlite3.connect(self._db_path)
            conn.execute(
                "CREATE TABLE IF NOT EXISTS alerts (id INTEGER PRIMARY KEY, ts REAL NOT NULL, kind TEXT NOT NULL, title TEXT, detail TEXT, severity INTEGER DEFAULT 1, acknowledged INTEGER DEFAULT 0)"
            )
            conn.commit(); conn.close()
        except Exception:
            pass

    def _eval(self, topic, payload):
        try: data = json.loads(payload)
        except: data = {"raw": payload}
        ctx = {"topic": topic, "payload": data, "hour": int(time.strftime("%H"))}
        for r in self.rules:
            if r["fn"](ctx):
                # Persist alert row
                try:
                    conn = sqlite3.connect(self._db_path)
                    conn.execute(
                        "INSERT INTO alerts(ts, kind, title, detail, severity) VALUES(?,?,?,?,?)",
                        (time.time(), ctx.get("topic","custom"), str(ctx.get("topic")), json.dumps(ctx.get("payload")), 1),
                    )
                    conn.commit(); conn.close()
                except Exception:
                    pass
                for action in r["do"]:
                    self.bus.pub("alerts/exec", {"action": action, "ctx": ctx})
