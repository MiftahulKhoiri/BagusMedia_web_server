import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "app", "database.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
    print("Kolom role berhasil ditambahkan")
except:
    print("Kolom role sudah ada, dilewati")

conn.commit()
conn.close()