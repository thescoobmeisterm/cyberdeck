from .base import Tile
class MotionTile(Tile):
    topic = "cam/motion"
    def __init__(self, bus):
        super().__init__(bus, text="Motion\n—")
    def update(self, d):
        self.text = f"Motion\n{d.get('score',0):.2f}"
