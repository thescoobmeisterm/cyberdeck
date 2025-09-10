from .base import Tile
class FaceTile(Tile):
    topic = "cam/face"
    def __init__(self, bus):
        super().__init__(bus, text="Face\n—")
    def update(self, d):
        name = d.get("name","?")
        conf = d.get("conf",0)
        self.text = f"Face\n{name} ({conf:.2f})"
