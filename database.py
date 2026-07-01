import sqlite3
from datetime import datetime, date

DB_PATH = "attendance.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id  TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            roll_no     TEXT,
            created_at  TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id  TEXT NOT NULL,
            date        TEXT NOT NULL,
            time_in     TEXT NOT NULL,
            status      TEXT NOT NULL DEFAULT 'Present',
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            UNIQUE(student_id, date)
        )
    """)

    conn.commit()
    conn.close()
    print("Database ready!")

def add_student(student_id, name, roll_no=""):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO students (student_id, name, roll_no, created_at) VALUES (?, ?, ?, ?)",
        (student_id, name, roll_no, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()

def get_all_students():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT student_id, name, roll_no FROM students")
    rows = cur.fetchall()
    conn.close()
    return rows

def already_marked_today(student_id):
    conn = get_connection()
    cur = conn.cursor()
    today = date.today().isoformat()
    cur.execute(
        "SELECT 1 FROM attendance WHERE student_id = ? AND date = ?",
        (student_id, today),
    )
    result = cur.fetchone()
    conn.close()
    return result is not None

def mark_attendance(student_id):
    if already_marked_today(student_id):
        return False
    conn = get_connection()
    cur = conn.cursor()
    now = datetime.now()
    cur.execute(
        "INSERT INTO attendance (student_id, date, time_in, status) VALUES (?, ?, ?, ?)",
        (student_id, now.date().isoformat(), now.strftime("%H:%M:%S"), "Present"),
    )
    conn.commit()
    conn.close()
    return True

def get_attendance_for_date(target_date=None):
    if target_date is None:
        target_date = date.today().isoformat()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.student_id, s.name, s.roll_no, a.time_in, a.status
        FROM students s
        LEFT JOIN attendance a ON s.student_id = a.student_id AND a.date = ?
        ORDER BY s.name
    """, (target_date,))
    rows = cur.fetchall()
    conn.close()
    return rows