from .base import Tile
class DbMeterTile(Tile):
    topic = "audio/level"
    def __init__(self, bus):
        super().__init__(bus, text="dB\n--")
        self.font_size = "24sp"
    def update(self, d):
        self.text = f"dB\n{d.get('db',-99):.1f}"
