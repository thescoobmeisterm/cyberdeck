import time, json
import paho.mqtt.client as mqtt

try:
    import board, busio
    import adafruit_bme280
except Exception:
    board = busio = adafruit_bme280 = None


def main():
    cli = mqtt.Client(); cli.connect("localhost",1883,60); cli.loop_start()
    sensor = None
    if board and busio and adafruit_bme280:
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c)
        except Exception:
            sensor = None
    while True:
        if sensor:
            try:
                payload = {
                    "temp_c": float(sensor.temperature),
                    "humidity": float(sensor.humidity),
                    "pressure": float(sensor.pressure),
                    "ts": time.time(),
                }
                cli.publish("env/bme280", json.dumps(payload))
            except Exception:
                pass
        time.sleep(5)


if __name__ == "__main__":
    main()
