import sqlite3
from config import DB_PATH

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_conn() as conn:
        conn.executescript(open("schema.sql").read())

def save_entry(user_id, mood, work_hours, sleep_hours, comment=""):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO entries (user_id, mood, work_hours, sleep_hours, comment)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, mood, work_hours, sleep_hours, comment)
        )

def get_entries(user_id, days=7):
    with get_conn() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            """SELECT * FROM entries
               WHERE user_id = ?
                 AND date(created_at) >= date('now', ?)
               ORDER BY created_at DESC""",
            (user_id, f"-{days} days")
        )
        return cur.fetchall()

def get_all_entries(user_id):
    with get_conn() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT * FROM entries WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        return cur.fetchall()

def clear_entries(user_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM entries WHERE user_id = ?", (user_id,))

def get_reminder(user_id):
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT hour, minute FROM reminders WHERE user_id = ?", (user_id,)
        )
        return cur.fetchone()

def set_reminder(user_id, hour, minute):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO reminders (user_id, hour, minute)
               VALUES (?, ?, ?)
               ON CONFLICT(user_id) DO UPDATE SET hour=excluded.hour, minute=excluded.minute""",
            (user_id, hour, minute)
        )

def get_all_users():
    with get_conn() as conn:
        cur = conn.execute("SELECT DISTINCT user_id FROM reminders")
        return [row[0] for row in cur.fetchall()]