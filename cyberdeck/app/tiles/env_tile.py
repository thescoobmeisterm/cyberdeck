from .base import Tile


class EnvTile(Tile):
    topic = "env/bme280"
    def __init__(self, bus):
        super().__init__(bus, text="Env\n--°C --%")
        self.font_size = "18sp"
    def update(self, d):
        t = d.get("temp_c", "--")
        h = d.get("humidity", "--")
        self.text = f"Env\n{t}°C {h}%"
