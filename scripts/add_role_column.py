import sqlite3

db_path = "app/database.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
    print("Kolom 'role' berhasil ditambahkan.")
except Exception as e:
    print("Kolom mungkin sudah ada:", e)

conn.commit()
conn.close()