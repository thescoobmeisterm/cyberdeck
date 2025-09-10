import yaml, os

def load_config():
    path = os.path.expanduser("config/deck.yaml")
    with open(path) as f:
        return yaml.safe_load(f)
