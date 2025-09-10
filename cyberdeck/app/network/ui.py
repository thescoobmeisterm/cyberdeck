from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label


def open_network_popup(bus):
    layout = BoxLayout(orientation='vertical', spacing=8, padding=8)
    inputs = BoxLayout(size_hint=(1, None), height=48, spacing=8)
    ssid_in = TextInput(hint_text="SSID", multiline=False)
    psk_in = TextInput(hint_text="Password", multiline=False, password=True)
    inputs.add_widget(ssid_in)
    inputs.add_widget(psk_in)

    btns = BoxLayout(size_hint=(1, None), height=48, spacing=8)
    scan_btn = Button(text="Scan")
    connect_btn = Button(text="Connect")
    close_btn = Button(text="Close")
    btns.add_widget(scan_btn)
    btns.add_widget(connect_btn)
    btns.add_widget(close_btn)

    out_sv = ScrollView(size_hint=(1, 1))
    out_lbl = Label(text="Ready", size_hint_y=None)
    out_lbl.bind(texture_size=lambda _i, s: setattr(out_lbl, 'height', s[1]))
    out_sv.add_widget(out_lbl)

    def append(text):
        out_lbl.text = (out_lbl.text + "\n" + text) if out_lbl.text else text

    def do_scan(_):
        append("Scanning Wi‑Fi...")
        bus.pub("net/scan", {})

    def do_connect(_):
        ssid = ssid_in.text.strip(); psk = psk_in.text
        if ssid and psk:
            append(f"Connecting to {ssid}...")
            bus.pub("net/connect", {"ssid": ssid, "psk": psk})
        else:
            append("Enter SSID and password")

    def on_scan_result(_topic, payload):
        try:
            import json
            d = json.loads(payload)
            if d.get("ok"):
                text = d.get("raw", "")
                append(text[:4000])
            else:
                append("Scan error: " + str(d.get("raw")))
        except Exception:
            append("(malformed scan result)")

    def on_connect_result(_topic, payload):
        try:
            import json
            d = json.loads(payload)
            append("Connect: " + ("OK" if d.get("ok") else ("ERR " + str(d.get("error")))))
        except Exception:
            append("(malformed connect result)")

    bus.sub("net/scan_result", on_scan_result)
    bus.sub("net/connect_result", on_connect_result)
    scan_btn.bind(on_press=do_scan)
    connect_btn.bind(on_press=do_connect)
    close_btn.bind(on_press=lambda _b: popup.dismiss())
    popup = Popup(title='Network', content=layout, size_hint=(0.95, 0.9))
    layout.add_widget(inputs)
    layout.add_widget(out_sv)
    layout.add_widget(btns)
    popup.open()
