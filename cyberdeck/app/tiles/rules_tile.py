from .base import Tile
from app.alerts.rules_ui import open_rules_editor


class RulesTile(Tile):
    topic = None
    def __init__(self, bus):
        super().__init__(bus, text="Rules\nEdit")
        self.font_size = "18sp"
    def on_press(self):
        open_rules_editor(self.bus)
