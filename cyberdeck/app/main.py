from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.lang import Builder

from app.bus.mqtt_client import Bus
from app.config import load_config
from app.tiles.system_tile import SystemTile
from app.tiles.db_meter_tile import DbMeterTile
from app.tiles.motion_tile import MotionTile
from app.tiles.face_tile import FaceTile
from app.alerts.engine import AlertEngine


TILES = {
    "system": SystemTile,
    "db_meter": DbMeterTile,
    "motion": MotionTile,
    "face": FaceTile,
}


class Deck(GridLayout):
    pass


class CyberdeckApp(App):
    def build(self):
        # Load kv definitions for widgets in this module
        Builder.load_file("app/deck.kv")

        self.cfg = load_config()
        self.bus = Bus(self.cfg["mqtt"])
        self.alerts = AlertEngine(self.bus, self.cfg.get("alerts", {}))

        grid_cfg = self.cfg["ui"]["grid"]
        self.root = Deck(cols=grid_cfg["cols"], spacing=grid_cfg["gap_dp"]) 
        for name in self.cfg["ui"]["tiles"]:
            cls = TILES.get(name)
            if cls:
                self.root.add_widget(cls(self.bus))
        Clock.schedule_interval(lambda dt: None, 0.5)
        return self.root


if __name__ == "__main__":
    CyberdeckApp().run()
