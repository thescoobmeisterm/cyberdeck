import time, json, subprocess, socket
import psutil
import paho.mqtt.client as mqtt


def get_ips():
    ips = {}
    for iface, addrs in psutil.net_if_addrs().items():
        for a in addrs:
            if a.family == socket.AF_INET:
                ips.setdefault(iface, []).append(a.address)
    return ips


def get_wifi_info(iface: str = "wlan0"):
    ssid = None
    rssi = None
    try:
        ssid = subprocess.check_output(["iwgetid", "-r"]).decode().strip() or None
    except Exception:
        pass
    try:
        out = subprocess.check_output(["iw", "dev", iface, "link"]).decode()
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("signal:"):
                # e.g., signal: -46 dBm
                parts = line.split()
                rssi = int(parts[1])
                break
    except Exception:
        pass
    return {"ssid": ssid, "rssi": rssi}


def main():
    cli = mqtt.Client(); cli.connect("localhost",1883,60); cli.loop_start()
    iface = "wlan0"
    # Allow scan via MQTT command
    def on_msg(_c,_u,msg):
        if msg.topic == "net/scan":
            try:
                out = subprocess.check_output(["iw", "dev", iface, "scan"], stderr=subprocess.STDOUT, text=True, timeout=10)
                cli.publish("net/scan_result", json.dumps({"ok": True, "raw": out, "ts": time.time()}))
            except subprocess.CalledProcessError as e:
                cli.publish("net/scan_result", json.dumps({"ok": False, "raw": e.output, "ts": time.time()}))
            except Exception as e:
                cli.publish("net/scan_result", json.dumps({"ok": False, "raw": str(e), "ts": time.time()}))
        elif msg.topic == "net/connect":
            try:
                d = json.loads(msg.payload)
                ssid = d.get("ssid"); psk = d.get("psk")
                if ssid and psk:
                    # Use nmcli to connect
                    subprocess.check_call(["nmcli", "dev", "wifi", "connect", ssid, "password", psk, "ifname", iface])
                    cli.publish("net/connect_result", json.dumps({"ok": True, "ssid": ssid}))
                else:
                    cli.publish("net/connect_result", json.dumps({"ok": False, "error": "missing ssid/psk"}))
            except subprocess.CalledProcessError as e:
                cli.publish("net/connect_result", json.dumps({"ok": False, "error": str(e)}))
            except Exception as e:
                cli.publish("net/connect_result", json.dumps({"ok": False, "error": str(e)}))
    cli.on_message = on_msg
    cli.subscribe("net/scan")
    cli.subscribe("net/connect")
    while True:
        payload = {
            "ips": get_ips(),
            "wifi": get_wifi_info(iface),
            "ts": time.time(),
        }
        cli.publish("net/status", json.dumps(payload))
        time.sleep(5)


if __name__ == "__main__":
    main()
