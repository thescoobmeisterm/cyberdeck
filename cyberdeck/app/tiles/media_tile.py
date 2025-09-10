import os, glob
from .base import Tile
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label


class MediaTile(Tile):
    topic = "cam/recorded"
    def __init__(self, bus):
        super().__init__(bus, text="Media\n—")
        self.font_size = "18sp"
        self.count = 0
    def update(self, d):
        self.count += 1
        self.text = f"Media\n{self.count} clips"
    def on_press(self):
        base = os.path.expanduser("~/deck/media")
        files = sorted(glob.glob(os.path.join(base, "rec", "**", "*.mp4"), recursive=True), key=os.path.getmtime, reverse=True)[:20]
        snaps = sorted(glob.glob(os.path.join(base, "snap", "*.jpg")), key=os.path.getmtime, reverse=True)[:10]
        layout = BoxLayout(orientation='vertical', spacing=8, padding=8)
        sv = ScrollView(size_hint=(1,1))
        inner = BoxLayout(orientation='vertical', size_hint_y=None, spacing=4)
        inner.bind(minimum_height=inner.setter('height'))
        if not files and not snaps:
            inner.add_widget(Label(text="No media yet", size_hint_y=None, height=24))
        else:
            for p in files:
                inner.add_widget(Label(text=p, size_hint_y=None, height=24))
            for p in snaps:
                inner.add_widget(Label(text=p, size_hint_y=None, height=24))
        sv.add_widget(inner)
        layout.add_widget(sv)
        Popup(title='Media', content=layout, size_hint=(0.95,0.9)).open()
