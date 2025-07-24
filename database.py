import sqlite3
import csv
from datetime import datetime
import os

DB_FILE = os.environ.get("DB_FILE", "scraper.db")

def connect():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = connect()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS profiles(
        url TEXT PRIMARY KEY,
        name TEXT,
        phone TEXT,
        about TEXT,
        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS metadata(
        key TEXT PRIMARY KEY,
        value TEXT
    )""")
    conn.commit()
    conn.close()

def profile_exists(url):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT url FROM profiles WHERE url=?", (url,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists

def save_profile(profile):
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO profiles(url,name,phone,about) VALUES(?,?,?,?)",
                (profile["url"], profile["name"], profile["phone"], profile["about"]))
    conn.commit()
    conn.close()

def export_csv():
    filename = "output.csv"
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT url,name,phone,about,scraped_at FROM profiles")
    rows = cur.fetchall()
    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["URL","Name","Phone","About","Scraped_At"])
        writer.writerows(rows)
    conn.close()
    return filename

def update_last_run():
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO metadata(key,value) VALUES('last_run',?)", (datetime.utcnow().isoformat(),))
    conn.commit()
    conn.close()

def get_last_run():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT value FROM metadata WHERE key='last_run'")
    row = cur.fetchone()
    conn.close()
    return row[0] if row else "Never"

def get_total_records():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM profiles")
    total = cur.fetchone()[0]
    conn.close()
    return total

init_db()
