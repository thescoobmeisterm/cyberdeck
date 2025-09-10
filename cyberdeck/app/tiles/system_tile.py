from .base import Tile


class SystemTile(Tile):
    topic = "sys/health"
    def __init__(self, bus):
        super().__init__(bus, text="SYS\n-- °C")
        self.font_size = "20sp"
    def update(self, d):
        self.text = f"CPU {d.get('cpu',0):.0f}%\nRAM {d.get('ram',0):.0f}%\n{d.get('temp_c','--')}°C"
