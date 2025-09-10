from .base import Tile


class PrivacyTile(Tile):
    topic = "privacy/state"
    def __init__(self, bus):
        super().__init__(bus, text="Privacy\nOff")
        self.font_size = "18sp"
    def update(self, d):
        state = bool(d.get("on", False))
        self.text = f"Privacy\n{'On' if state else 'Off'}"
    def on_press(self):
        self.bus.pub("ui/privacy/toggle", {"ts": 0})
