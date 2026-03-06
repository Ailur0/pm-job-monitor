import sqlite3
from datetime import datetime

DB_PATH = "jobs.db"


def init_db():
    """Initialize the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT UNIQUE,
            title TEXT,
            company TEXT,
            location TEXT,
            platform TEXT,
            url TEXT,
            status TEXT DEFAULT 'seen',  -- seen / applied / skipped
            seen_at TIMESTAMP,
            applied_at TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_stats (
            date TEXT PRIMARY KEY,
            applies_count INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Database initialized.")


def is_job_seen(job_id: str) -> bool:
    """Check if we've already seen this job."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM jobs WHERE job_id = ?", (job_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def save_job(job_id: str, title: str, company: str, location: str, platform: str, url: str, **kwargs):
    """Save a newly seen job."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO jobs (job_id, title, company, location, platform, url, seen_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (job_id, title, company, location, platform, url, datetime.now()))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Already exists
    conn.close()


def mark_applied(job_id: str):
    """Mark a job as applied."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE jobs SET status = 'applied', applied_at = ? WHERE job_id = ?
    """, (datetime.now(), job_id))
    conn.commit()
    conn.close()


def get_today_apply_count() -> int:
    """Get how many jobs we've applied to today."""
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM jobs 
        WHERE status = 'applied' AND DATE(applied_at) = ?
    """, (today,))
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_all_applications():
    """Get all applications for review."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, company, platform, status, seen_at, applied_at 
        FROM jobs ORDER BY seen_at DESC LIMIT 50
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows
