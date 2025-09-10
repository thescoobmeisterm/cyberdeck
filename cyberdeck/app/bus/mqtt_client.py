import json, threading
import paho.mqtt.client as mqtt


class Bus:
    def __init__(self, cfg):
        self._subs = {}
        self.client = mqtt.Client()
        self.client.on_message = self._on_msg
        self.client.connect(cfg["host"], cfg["port"], 60)
        threading.Thread(target=self.client.loop_forever, daemon=True).start()

    def sub(self, topic, cb):
        self._subs.setdefault(topic, []).append(cb)
        self.client.subscribe(topic)

    def pub(self, topic, payload):
        if not isinstance(payload, (str, bytes)):
            payload = json.dumps(payload)
        self.client.publish(topic, payload)

    def _on_msg(self, _c, _u, msg):
        for pat, cbs in self._subs.items():
            if mqtt.topic_matches_sub(pat, msg.topic):
                for cb in cbs:
                    cb(msg.topic, msg.payload)
