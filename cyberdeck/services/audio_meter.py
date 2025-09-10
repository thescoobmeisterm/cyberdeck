import json, time, numpy as np, sounddevice as sd, paho.mqtt.client as mqtt


RATE, CHUNK = 48000, 2048

def spl_db(samples, ref=2e-5):
    rms = np.sqrt(np.mean(np.square(samples)) + 1e-12)
    return 20*np.log10(rms/ref)


def main():
    cli = mqtt.Client(); cli.connect("localhost",1883,60); cli.loop_start()
    with sd.InputStream(samplerate=RATE, channels=1, blocksize=CHUNK, dtype='float32') as stream:
        while True:
            frames, _ = stream.read(CHUNK)
            db = float(spl_db(frames[:,0]))
            cli.publish("audio/level", json.dumps({"db": db, "rms": float(np.mean(np.abs(frames))), "ts": time.time()}))


if __name__ == "__main__":
    main()
