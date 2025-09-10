import ast, time, json
from .rules import compile_rules


class AlertEngine:
    def __init__(self, bus, cfg):
        self.bus = bus
        self.rules = compile_rules(cfg.get("rules", []))
        self.bus.sub("#", self._eval)

    def _eval(self, topic, payload):
        try: data = json.loads(payload)
        except: data = {"raw": payload}
        ctx = {"topic": topic, "payload": data, "hour": int(time.strftime("%H"))}
        for r in self.rules:
            if r["fn"](ctx):
                for action in r["do"]:
                    self.bus.pub("alerts/exec", {"action": action, "ctx": ctx})
