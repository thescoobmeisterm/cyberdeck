import sqlite3, os

def db(path):
    p = os.path.expanduser(path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    conn = sqlite3.connect(p, check_same_thread=False)
    return conn
