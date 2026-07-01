import sys
import os
import pandas as pd
from datetime import date
import database

REPORTS_DIR = "reports"

def daily_report(target_date=None):
    target_date = target_date or date.today().isoformat()
    rows = database.get_attendance_for_date(target_date)

    df = pd.DataFrame(rows, columns=["student_id", "name", "roll_no", "time_in", "status"])
    df["status"] = df["status"].fillna("Absent")
    df["time_in"] = df["time_in"].fillna("-")

    os.makedirs(REPORTS_DIR, exist_ok=True)
    out_path = os.path.join(REPORTS_DIR, f"attendance_{target_date}.csv")
    df.to_csv(out_path, index=False)

    present = (df["status"] == "Present").sum()
    total = len(df)

    print(f"\nAttendance Report — {target_date}")
    print(df.to_string(index=False))
    print(f"\nPresent: {present}/{total} ({(present/total*100 if total else 0):.1f}%)")
    print(f"Saved: {out_path}")

def summary_report():
    conn = database.get_connection()
    total_days = conn.execute(
        "SELECT COUNT(DISTINCT date) FROM attendance"
    ).fetchone()[0] or 1

    df = pd.read_sql_query("""
        SELECT s.student_id, s.name, s.roll_no, COUNT(a.id) as days_present
        FROM students s
        LEFT JOIN attendance a ON s.student_id = a.student_id
        GROUP BY s.student_id
        ORDER BY s.name
    """, conn)
    conn.close()

    df["attendance_pct"] = (df["days_present"] / total_days * 100).round(1)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    out_path = os.path.join(REPORTS_DIR, "attendance_summary.csv")
    df.to_csv(out_path, index=False)

    print(f"\nOverall Summary ({total_days} din ka record)")
    print(df.to_string(index=False))
    print(f"\nSaved: {out_path}")

if __name__ == "__main__":
    database.init_db()
    if len(sys.argv) > 1 and sys.argv[1] == "--summary":
        summary_report()
    elif len(sys.argv) > 1:
        daily_report(sys.argv[1])
    else:
        daily_report()