from .base import Tile


class AlertsTile(Tile):
    topic = "alerts/exec"
    def __init__(self, bus):
        super().__init__(bus, text="Alerts\n0")
        self.count = 0
        self.font_size = "18sp"
    def update(self, d):
        self.count += 1
        self.text = f"Alerts\n{self.count}"
