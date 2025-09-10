from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.lang import Builder
import os

from app.bus.mqtt_client import Bus
from app.config import load_config
from app.tiles.system_tile import SystemTile
from app.tiles.db_meter_tile import DbMeterTile
from app.tiles.motion_tile import MotionTile
from app.tiles.face_tile import FaceTile
from app.alerts.engine import AlertEngine
from app.tiles.network_tile import NetworkTile
from app.tiles.jobs_tile import JobsTile
from app.tiles.alerts_tile import AlertsTile
from app.tiles.privacy_tile import PrivacyTile
from app.tiles.env_tile import EnvTile
from app.tiles.rules_tile import RulesTile
from app.tiles.media_tile import MediaTile


TILES = {
    "system": SystemTile,
    "db_meter": DbMeterTile,
    "motion": MotionTile,
    "face": FaceTile,
    "network": NetworkTile,
    "jobs": JobsTile,
    "alerts": AlertsTile,
    "privacy": PrivacyTile,
    "env": EnvTile,
    "rules": RulesTile,
    "media": MediaTile,
}


class Deck(GridLayout):
    pass


class CyberdeckApp(App):
    def build(self):
        # Load kv definitions for widgets in this module
        Builder.load_file("app/deck.kv")

        self.cfg = load_config()
        # Export DB path for services/helpers
        try:
            os.environ["DECK_DB_PATH"] = os.path.expanduser(self.cfg["paths"]["db"])  # type: ignore[index]
            os.environ["DECK_CONFIG_PATH"] = os.path.abspath("config/deck.yaml")
        except Exception:
            pass
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
