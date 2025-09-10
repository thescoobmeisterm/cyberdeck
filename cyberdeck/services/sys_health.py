import time, json, psutil, subprocess, paho.mqtt.client as mqtt


def get_temp():
    try:
        out = subprocess.check_output(["vcgencmd","measure_temp"]).decode()
        return float(out.split('=')[1].split("'")[0])
    except: return None


def main():
    c = mqtt.Client(); c.connect("localhost", 1883, 60); c.loop_start()
    while True:
        payload = {
            "cpu": psutil.cpu_percent(),
            "ram": psutil.virtual_memory().percent,
            "temp_c": get_temp(),
            "freq_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else None,
            "throttle": False,
            "ts": time.time()
        }
        c.publish("sys/health", json.dumps(payload))
        time.sleep(1)


if __name__ == "__main__":
    main()
