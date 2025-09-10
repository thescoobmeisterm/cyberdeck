from .base import Tile
from app.jobs.ui import open_jobs_popup


class JobsTile(Tile):
    topic = "jobs/result"
    def __init__(self, bus):
        super().__init__(bus, text="Jobs\n—")
        self.font_size = "18sp"
    def update(self, d):
        name = d.get("name", "?")
        ok = d.get("ok")
        status = "ok" if ok else ("err" if ok is False else "—")
        self.text = f"Jobs\n{name}: {status}"
    def on_press(self):
        open_jobs_popup(self.bus)
