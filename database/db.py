import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "civicguard.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def create_table():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS moderation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_text TEXT,
            toxic REAL,
            severe_toxic REAL,
            obscene REAL,
            threat REAL,
            insult REAL,
            identity_hate REAL,
            decision TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()

def log_result(text, scores, decision):
    conn = get_connection()

    conn.execute("""
        INSERT INTO moderation_logs
        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        text,
        scores["toxic"],
        scores["severe_toxic"],
        scores["obscene"],
        scores["threat"],
        scores["insult"],
        scores["identity_hate"],
        decision,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()