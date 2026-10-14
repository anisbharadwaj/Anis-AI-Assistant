"""Audit logging for important automation actions.
Writes simple append-only logs to a file and also stores audit entries in the
SQLite preferences DB if available.
"""
from datetime import datetime
import os
from memory import database
from pathlib import Path

LOG_PATH = Path(os.getenv("AUDIT_LOG_PATH", "anis_ai_audit.log"))


def log_action(action: str, details: str, success: bool = True):
    timestamp = datetime.utcnow().isoformat()
    line = f"{timestamp} | {action} | success={success} | {details}\n"
    try:
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass
    # also record in sqlite audit table
    try:
        conn = database.get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT,
                action TEXT,
                success INTEGER,
                details TEXT
            )
            """
        )
        cur.execute("INSERT INTO audit (ts, action, success, details) VALUES (?, ?, ?, ?)", (timestamp, action, int(success), details))
        conn.commit()
    except Exception:
        pass
