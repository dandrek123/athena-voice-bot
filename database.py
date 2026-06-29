import sqlite3
from datetime import datetime

DB_NAME = "athena.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario TEXT,
            status TEXT,
            quality_score INTEGER,
            duration_seconds REAL,
            warnings_count INTEGER,
            transcript TEXT,
            summary TEXT,
            report_path TEXT,
            transcript_path TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_call_report(
    scenario,
    status,
    quality_score,
    duration_seconds,
    warnings_count,
    transcript,
    summary,
    report_path=None,
    transcript_path=None
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO calls (
            scenario,
            status,
            quality_score,
            duration_seconds,
            warnings_count,
            transcript,
            summary,
            report_path,
            transcript_path,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        scenario,
        status,
        quality_score,
        duration_seconds,
        warnings_count,
        transcript,
        summary,
        report_path,
        transcript_path,
        datetime.now().isoformat(timespec="seconds")
    ))

    conn.commit()
    conn.close()


def get_all_calls():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM calls
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def search_calls(scenario=None, status=None, warnings_only=False, min_quality=None):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM calls WHERE 1=1"
    params = []

    if scenario:
        query += " AND scenario LIKE ?"
        params.append(f"%{scenario}%")

    if status:
        query += " AND status LIKE ?"
        params.append(f"%{status}%")

    if warnings_only:
        query += " AND warnings_count > 0"

    if min_quality:
        query += " AND quality_score >= ?"
        params.append(int(min_quality))

    query += " ORDER BY created_at DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return rows