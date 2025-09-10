import json, time
import paho.mqtt.client as mqtt


class PrivacyService:
    def __init__(self):
        self.state = False
        self.cli = mqtt.Client()
        self.cli.on_message = self.on_msg
        self.cli.connect("localhost", 1883, 60)
        self.cli.subscribe("privacy/set")
        self.cli.subscribe("ui/privacy/toggle")

    def publish_state(self):
        self.cli.publish("privacy/state", json.dumps({"on": self.state, "ts": time.time()}))

    def on_msg(self, _c,_u,msg):
        try:
            if msg.topic == "privacy/set":
                d = json.loads(msg.payload)
                self.state = bool(d.get("on"))
            elif msg.topic == "ui/privacy/toggle":
                self.state = not self.state
        except Exception:
            pass
        self.publish_state()

    def run(self):
        # Publish initial state
        self.publish_state()
        self.cli.loop_forever()


def main():
    PrivacyService().run()


if __name__ == "__main__":
    main()
