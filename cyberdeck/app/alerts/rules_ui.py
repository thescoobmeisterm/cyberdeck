import os, yaml
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button


def open_rules_editor(bus, config_path: str = "config/deck.yaml"):
    path = os.path.expanduser(config_path)
    try:
        with open(path) as f:
            cfg = yaml.safe_load(f)
    except Exception:
        cfg = {}
    rules = (cfg.get("alerts") or {}).get("rules", [])
    initial = yaml.safe_dump(rules, sort_keys=False)

    layout = BoxLayout(orientation='vertical', spacing=8, padding=8)
    ti = TextInput(text=initial, multiline=True, size_hint=(1, 1))
    btns = BoxLayout(size_hint=(1, None), height=48, spacing=8)
    save_btn = Button(text="Save & Reload")
    cancel_btn = Button(text="Cancel")
    btns.add_widget(cancel_btn)
    btns.add_widget(save_btn)
    layout.add_widget(ti)
    layout.add_widget(btns)
    pop = Popup(title='Rules Editor', content=layout, size_hint=(0.95, 0.9))

    def on_save(_):
        try:
            new_rules = yaml.safe_load(ti.text) or []
            # Send to engine; it will persist and reload
            bus.pub("alerts/rules/set", {"rules": new_rules})
            pop.dismiss()
        except Exception:
            pop.dismiss()

    def on_cancel(_):
        pop.dismiss()

    save_btn.bind(on_press=on_save)
    cancel_btn.bind(on_press=on_cancel)
    pop.open()
