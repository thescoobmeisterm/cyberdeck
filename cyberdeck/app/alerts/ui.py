import os, sqlite3
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView


def show_alerts_popup(db_path_env: str = "DECK_DB_PATH"):
    db_path = os.environ.get(db_path_env) or os.path.expanduser("~/deck/db.sqlite")
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT ts, kind, title, severity FROM alerts ORDER BY ts DESC LIMIT 50")
        rows = cur.fetchall()
        conn.close()
    except Exception:
        rows = []
    layout = BoxLayout(orientation='vertical', spacing=8, padding=8)
    sv = ScrollView(size_hint=(1, 1))
    inner = BoxLayout(orientation='vertical', size_hint_y=None, spacing=4)
    inner.bind(minimum_height=inner.setter('height'))
    for ts, kind, title, sev in rows:
        inner.add_widget(Label(text=f"{kind} | {title} | sev={sev}", size_hint_y=None, height=24))
    if not rows:
        inner.add_widget(Label(text="No alerts yet", size_hint_y=None, height=24))
    sv.add_widget(inner)
    layout.add_widget(sv)
    Popup(title='Alerts', content=layout, size_hint=(0.9, 0.8)).open()
