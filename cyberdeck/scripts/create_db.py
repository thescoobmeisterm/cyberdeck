#!/usr/bin/env python3
import os, sqlite3

def main():
    path = os.path.expanduser("~/deck/db.sqlite")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    with open(os.path.join(os.path.dirname(__file__), "..", "db", "schema.sql")) as f:
        conn.executescript(f.read())
    conn.commit()
    print("DB initialized at", path)

if __name__ == "__main__":
    main()
