from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label


def open_jobs_popup(bus):
    layout = BoxLayout(orientation='vertical', spacing=8, padding=8)
    btns = BoxLayout(size_hint=(1, None), height=48, spacing=8)
    out_sv = ScrollView(size_hint=(1, 1))
    out_lbl = Label(text="Ready", size_hint_y=None)
    out_lbl.bind(texture_size=lambda _i, s: setattr(out_lbl, 'height', s[1]))
    out_sv.add_widget(out_lbl)

    def append(text):
        out_lbl.text = (out_lbl.text + "\n" + text) if out_lbl.text else text

    def run_lan_scan(_):
        append("Running LAN scan...")
        bus.pub("jobs/run", {"name": "lan_scan"})

    lan_btn = Button(text="LAN Scan")
    close_btn = Button(text="Close")
    btns.add_widget(lan_btn)
    btns.add_widget(close_btn)
    layout.add_widget(out_sv)
    layout.add_widget(btns)
    pop = Popup(title='Jobs', content=layout, size_hint=(0.95, 0.9))

    def on_result(_topic, payload):
        try:
            import json
            d = json.loads(payload)
            if d.get("ok"):
                append(d.get("out", "(no output)"))
            else:
                append("ERROR: " + str(d.get("out") or d.get("error")))
        except Exception:
            append("(malformed result)")

    bus.sub("jobs/result", on_result)
    lan_btn.bind(on_press=run_lan_scan)
    close_btn.bind(on_press=lambda _b: pop.dismiss())
    pop.open()
