from kivy.uix.button import Button
import json, time


class Tile(Button):
    topic = None
    def __init__(self, bus, **kw):
        super().__init__(**kw)
        self.bus = bus
        if self.topic:
            self.bus.sub(self.topic, self.on_bus)

    def on_bus(self, topic, payload):
        try:
            data = json.loads(payload.decode() if isinstance(payload, bytes) else payload)
        except Exception:
            data = {"raw": payload}
        self.update(data)

    def update(self, data):
        pass

    def long_press(self):
        self.bus.pub("ui/cmd/open", {"tile": self.__class__.__name__, "ts": time.time()})
