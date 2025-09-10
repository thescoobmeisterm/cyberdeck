#!/usr/bin/env python3
import time, json, argparse
import paho.mqtt.client as mqtt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db_ref", type=float, required=True, help="Reference dB SPL from phone app")
    args = ap.parse_args()

    cli = mqtt.Client(); cli.connect("localhost",1883,60); cli.loop_start()
    print("Publish this adjustment into config/deck.yaml under audio.db_ref if needed.")
    # This tool just subscribes and shows current readings for manual alignment
    def on_msg(_c,_u,msg):
        try:
            d = json.loads(msg.payload)
        except Exception:
            return
        print(f"measured={d.get('db'):.1f} dB, target={args.db_ref:.1f} dB, offset={args.db_ref - d.get('db'):.1f} dB")
    cli.subscribe("audio/level")
    cli.on_message = on_msg
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
