import json, time, paho.mqtt.client as mqtt


# Placeholder: integrate 'face_recognition' or a tiny insightface later
def main():
    cli = mqtt.Client(); cli.connect("localhost",1883,60); cli.loop_start()
    while True:
        # TODO: implement capture -> detect -> encode -> match
        time.sleep(1)


if __name__ == "__main__":
    main()
