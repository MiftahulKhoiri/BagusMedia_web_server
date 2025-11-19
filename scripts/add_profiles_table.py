#!/usr/bin/env python3
# scripts/add_profiles_table.py
import sqlite3
import os
import sys
from datetime import datetime

# atur path database sesuai struktur proyek kamu
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "app", "database.db")  # sesuaikan jika beda

def backup_db(db_path):
    bak = db_path + ".bak-" + datetime.utcnow().strftime("%Y%m%d%H%M%S")
    try:
        import shutil
        shutil.copy2(db_path, bak)
        print(f"[OK] Backup dibuat: {bak}")
    except Exception as e:
        print("[WARN] Gagal membuat backup:", e)

def ensure_profiles_table(conn):
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        nama TEXT,
        email TEXT,
        jk TEXT,
        umur INTEGER,
        bio TEXT,
        foto TEXT,
        cover TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    conn.commit()
    print("[OK] Tabel profiles terbuat (atau sudah ada).")

def populate_profiles_for_existing_users(conn):
    cur = conn.cursor()
    # ambil semua user id dan username
    cur.execute("SELECT id, username FROM users")
    rows = cur.fetchall()
    inserted = 0
    for user_id, username in rows:
        # cek apakah profile sudah ada
        cur.execute("SELECT id FROM profiles WHERE user_id=?", (user_id,))
        if cur.fetchone():
            continue
        # buat profile dasar: nama = username
        cur.execute("""
            INSERT INTO profiles (user_id, nama, email, jk, umur, bio, foto, cover)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, username, "", "", None, "", "", ""))
        inserted += 1
    conn.commit()
    print(f"[OK] Profiles ditambahkan untuk {inserted} user yang belum punya profile.")

def main():
    if not os.path.exists(DB_PATH):
        print("Database tidak ditemukan di:", DB_PATH)
        sys.exit(1)

    print("Database:", DB_PATH)
    backup_db(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    try:
        ensure_profiles_table(conn)
        populate_profiles_for_existing_users(conn)
        print("[DONE] Migrasi profiles selesai.")
    except Exception as e:
        print("[ERROR] Terjadi error:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    main()