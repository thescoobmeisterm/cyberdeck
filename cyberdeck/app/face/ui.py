from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label


def open_face_popup(bus):
    layout = BoxLayout(orientation='vertical', spacing=8, padding=8)
    row = BoxLayout(size_hint=(1,None), height=48, spacing=8)
    name_in = TextInput(hint_text="Name", multiline=False)
    row.add_widget(name_in)
    btns = BoxLayout(size_hint=(1,None), height=48, spacing=8)
    enroll_btn = Button(text="Enroll (snapshot)")
    recognize_btn = Button(text="Recognize (snapshot)")
    close_btn = Button(text="Close")
    btns.add_widget(enroll_btn)
    btns.add_widget(recognize_btn)
    btns.add_widget(close_btn)
    status = Label(text="Ready")
    layout.add_widget(row)
    layout.add_widget(status)
    layout.add_widget(btns)
    pop = Popup(title='Face', content=layout, size_hint=(0.9, 0.4))

    def on_enroll(_):
        bus.pub("face/enroll_request", {"name": name_in.text.strip() or "?"})
        status.text = "Enrolling..."

    def on_recognize(_):
        bus.pub("face/recognize", {})
        status.text = "Recognizing..."

    def on_enroll_result(_t, payload):
        import json
        try:
            d = json.loads(payload)
            status.text = "Enroll: " + ("OK " + str(d.get("name")) if d.get("ok") else ("ERR " + str(d.get("error"))))
        except Exception:
            status.text = "Enroll: malformed"

    def on_recognize_result(_t, payload):
        import json
        try:
            d = json.loads(payload)
            if d.get("ok"):
                status.text = f"Recognized {d.get('name')} ({d.get('conf'):.2f})"
            else:
                status.text = "Not recognized"
        except Exception:
            status.text = "Recognize: malformed"

    bus.sub("face/enroll_result", on_enroll_result)
    bus.sub("face/recognize_result", on_recognize_result)
    enroll_btn.bind(on_press=on_enroll)
    recognize_btn.bind(on_press=on_recognize)
    close_btn.bind(on_press=lambda _b: pop.dismiss())
    pop.open()
