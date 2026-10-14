"""Local SQLite storage for preferences and optional history.
This module is intentionally small and synchronous; it will be called from
background threads or async tasks when integrated into the UI.
"""
import sqlite3
from pathlib import Path
from typing import Optional
import os

DB_PATH = os.getenv("DATABASE_PATH", "anis_ai.db")


def get_connection(path: Optional[str] = None):
    p = Path(path or DB_PATH)
    conn = sqlite3.connect(str(p))
    return conn


def initialize_db(path: Optional[str] = None):
    conn = get_connection(path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS preferences (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    return conn


def set_preference(key: str, value: str, path: Optional[str] = None):
    conn = get_connection(path)
    cur = conn.cursor()
    cur.execute("REPLACE INTO preferences (key, value) VALUES (?, ?)", (key, value))
    conn.commit()


def get_preference(key: str, path: Optional[str] = None) -> Optional[str]:
    conn = get_connection(path)
    cur = conn.cursor()
    cur.execute("SELECT value FROM preferences WHERE key = ?", (key,))
    row = cur.fetchone()
    return row[0] if row else None
