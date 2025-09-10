from .base import Tile
from app.face.ui import open_face_popup
class FaceTile(Tile):
    topic = "cam/face"
    def __init__(self, bus):
        super().__init__(bus, text="Face\n—")
    def update(self, d):
        name = d.get("name","?")
        conf = d.get("conf",0)
        self.text = f"Face\n{name} ({conf:.2f})"
    def on_press(self):
        open_face_popup(self.bus)
