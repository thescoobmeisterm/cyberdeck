from .base import Tile


class NetworkTile(Tile):
    topic = "net/status"
    def __init__(self, bus):
        super().__init__(bus, text="NET\n—")
        self.font_size = "18sp"
    def update(self, d):
        ssid = (d.get("wifi") or {}).get("ssid") or "?"
        ips = d.get("ips", {})
        ip = next(iter(ips.get("wlan0", []) or ips.get("eth0", []) or ["-"]))
        self.text = f"NET\n{ssid}\n{ip}"
