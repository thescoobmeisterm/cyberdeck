import sqlite3, os, threading

_conn = None
_lock = threading.Lock()

def db(path):
    p = os.path.expanduser(path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    conn = sqlite3.connect(p, check_same_thread=False)
    return conn

def get_conn():
    global _conn
    if _conn is not None:
        return _conn
    with _lock:
        if _conn is None:
            db_path = os.environ.get("DECK_DB_PATH", os.path.expanduser("~/deck/db.sqlite"))
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            _conn = sqlite3.connect(db_path, check_same_thread=False)
        return _conn
