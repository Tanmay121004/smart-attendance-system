from flask import Flask, render_template_string, request
from datetime import date, datetime
import database
import webbrowser
import threading

app = Flask(__name__)
database.init_db()

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart Attendance System</title>
    <meta http-equiv="refresh" content="10">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial; background: #0f0f1a; color: white; padding: 20px; }
        
        h1 { color: #00d4ff; text-align: center; font-size: 28px; padding: 20px 0; }
        
        .nav { display: flex; justify-content: center; gap: 10px; margin-bottom: 25px; }
        .nav a {
            padding: 10px 25px; border-radius: 25px; text-decoration: none;
            font-weight: bold; transition: 0.3s;
        }
        .nav a.active { background: #00d4ff; color: #0f0f1a; }
        .nav a:not(.active) { background: #1e1e3a; color: #00d4ff; border: 1px solid #00d4ff; }
        .nav a:hover { opacity: 0.8; }

        .stats { display: flex; gap: 15px; justify-content: center; margin: 20px 0; flex-wrap: wrap; }
        .card {
            background: #1e1e3a; padding: 20px 35px;
            border-radius: 12px; text-align: center;
            border: 1px solid #2a2a4a; min-width: 150px;
        }
        .card h2 { font-size: 38px; margin: 0; color: #00d4ff; }
        .card p { margin: 5px 0; color: #aaa; font-size: 13px; }

        .date-filter {
            display: flex; align-items: center; gap: 10px;
            justify-content: center; margin: 20px 0;
        }
        .date-filter input[type=date] {
            padding: 8px 15px; border-radius: 8px;
            border: 1px solid #00d4ff; background: #1e1e3a;
            color: white; font-size: 15px; cursor: pointer;
        }
        .date-filter button {
            padding: 8px 20px; border-radius: 8px;
            border: none; background: #00d4ff;
            color: #0f0f1a; font-weight: bold;
            cursor: pointer; font-size: 15px;
        }

        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th { background: #00d4ff; color: #0f0f1a; padding: 12px; font-size: 14px; }
        td { padding: 12px; border-bottom: 1px solid #2a2a4a; text-align: center; font-size: 14px; }
        tr:hover { background: #1e1e3a; }

        .present { color: #00ff88; font-weight: bold; }
        .absent  { color: #ff4444; font-weight: bold; }
        .new-badge {
            background: #ff9900; color: #0f0f1a;
            font-size: 11px; padding: 2px 8px;
            border-radius: 10px; font-weight: bold; margin-left: 6px;
        }

        .pct-bar-bg {
            background: #2a2a4a; border-radius: 10px;
            height: 10px; width: 100px; margin: auto;
        }
        .pct-bar {
            background: #00d4ff; border-radius: 10px; height: 10px;
        }

        .footer {
            text-align: center; color: #444;
            margin-top: 30px; font-size: 13px;
        }
        .section-title {
            color: #00d4ff; font-size: 18px;
            margin: 25px 0 10px; border-bottom: 1px solid #2a2a4a;
            padding-bottom: 8px;
        }
    </style>
</head>
<body>
    <h1>🎓 Smart Attendance System</h1>

    <!-- Navigation -->
    <div class="nav">
        <a href="/" class="{{ 'active' if page == 'home' else '' }}">📋 Today</a>
        <a href="/date" class="{{ 'active' if page == 'date' else '' }}">📅 Date Filter</a>
        <a href="/monthly" class="{{ 'active' if page == 'monthly' else '' }}">📊 Monthly Summary</a>
        <a href="/enrolled" class="{{ 'active' if page == 'enrolled' else '' }}">👥 Enrolled Students</a>
    </div>

    {% if page == 'home' %}
    <!-- TODAY PAGE -->
    <div class="stats">
        <div class="card"><h2>{{ present }}</h2><p>Present Today</p></div>
        <div class="card"><h2>{{ total - present }}</h2><p>Absent Today</p></div>
        <div class="card">
            <h2>{{ "%.0f"|format(present/total*100 if total else 0) }}%</h2>
            <p>Attendance</p>
        </div>
        <div class="card"><h2>{{ new_today }}</h2><p>New Enrollments Today</p></div>
    </div>

    <h3 class="section-title">📅 Today — {{ today }}</h3>
    <table>
        <tr><th>Roll No</th><th>Name</th><th>Time In</th><th>Status</th></tr>
        {% for row in rows %}
        <tr>
            <td>{{ row[2] }}</td>
            <td>
                {{ row[1] }}
                {% if row[5] %}<span class="new-badge">NEW</span>{% endif %}
            </td>
            <td>{{ row[3] or "-" }}</td>
            <td class="{{ 'present' if row[4] == 'Present' else 'absent' }}">
                {{ row[4] or "Absent" }}
            </td>
        </tr>
        {% endfor %}
    </table>

    {% elif page == 'date' %}
    <!-- DATE FILTER PAGE -->
    <h3 class="section-title">📅 Kisi bhi din ki attendance dekho</h3>
    <div class="date-filter">
        <form method="GET" action="/date" style="display:flex; gap:10px; align-items:center">
            <input type="date" name="d" value="{{ selected_date }}">
            <button type="submit">Dekho</button>
        </form>
    </div>

    <div class="stats">
        <div class="card"><h2>{{ present }}</h2><p>Present</p></div>
        <div class="card"><h2>{{ total - present }}</h2><p>Absent</p></div>
        <div class="card">
            <h2>{{ "%.0f"|format(present/total*100 if total else 0) }}%</h2>
            <p>Attendance</p>
        </div>
    </div>

    <table>
        <tr><th>Roll No</th><th>Name</th><th>Time In</th><th>Status</th></tr>
        {% for row in rows %}
        <tr>
            <td>{{ row[2] }}</td>
            <td>{{ row[1] }}</td>
            <td>{{ row[3] or "-" }}</td>
            <td class="{{ 'present' if row[4] == 'Present' else 'absent' }}">
                {{ row[4] or "Absent" }}
            </td>
        </tr>
        {% endfor %}
    </table>

    {% elif page == 'monthly' %}
    <!-- MONTHLY SUMMARY PAGE -->
    <h3 class="section-title">📊 Monthly Attendance Summary — {{ month }}</h3>
    <table>
        <tr>
            <th>Roll No</th><th>Name</th>
            <th>Days Present</th><th>Total Days</th><th>Attendance %</th>
        </tr>
        {% for row in rows %}
        <tr>
            <td>{{ row[2] }}</td>
            <td>{{ row[1] }}</td>
            <td>{{ row[3] }}</td>
            <td>{{ total_days }}</td>
            <td>
                {{ row[4] }}%
                <div class="pct-bar-bg">
                    <div class="pct-bar" style="width: {{ row[4] }}%"></div>
                </div>
            </td>
        </tr>
        {% endfor %}
    </table>

    {% elif page == 'enrolled' %}
    <!-- ENROLLED STUDENTS PAGE -->
    <h3 class="section-title">👥 All Enrolled Students</h3>
    <div class="stats">
        <div class="card"><h2>{{ total }}</h2><p>Total Students</p></div>
        <div class="card"><h2>{{ new_today }}</h2><p>Enrolled Today</p></div>
    </div>
    <table>
        <tr><th>Student ID</th><th>Name</th><th>Roll No</th><th>Enrolled On</th></tr>
        {% for row in rows %}
        <tr>
            <td>{{ row[0] }}</td>
            <td>
                {{ row[1] }}
                {% if row[3][:10] == today %}<span class="new-badge">NEW TODAY</span>{% endif %}
            </td>
            <td>{{ row[2] }}</td>
            <td>{{ row[3][:10] }}</td>
        </tr>
        {% endfor %}
    </table>
    {% endif %}

    <div class="footer">
        Auto refresh: har 10 seconds mein •
        Last updated: {{ now }}
    </div>
</body>
</html>
"""

def get_new_enrollments_today():
    conn = database.get_connection()
    today = date.today().isoformat()
    count = conn.execute(
        "SELECT COUNT(*) FROM students WHERE created_at LIKE ?", (f"{today}%",)
    ).fetchone()[0]
    conn.close()
    return count

@app.route("/")
def index():
    today = date.today().isoformat()
    rows_raw = database.get_attendance_for_date(today)
    students = database.get_all_students()
    present_count = sum(1 for r in rows_raw if r[4] == "Present")
    new_today = get_new_enrollments_today()

    # check if student enrolled today
    conn = database.get_connection()
    rows = []
    for r in rows_raw:
        enrolled_today = conn.execute(
            "SELECT created_at FROM students WHERE student_id=?", (r[0],)
        ).fetchone()
        is_new = enrolled_today and enrolled_today[0][:10] == today
        rows.append(r + (is_new,))
    conn.close()

    return render_template_string(HTML,
        page="home", rows=rows, today=today,
        present=present_count, total=len(students),
        new_today=new_today,
        now=datetime.now().strftime("%H:%M:%S")
    )

@app.route("/date")
def date_filter():
    selected = request.args.get("d", date.today().isoformat())
    rows = database.get_attendance_for_date(selected)
    students = database.get_all_students()
    present_count = sum(1 for r in rows if r[4] == "Present")
    return render_template_string(HTML,
        page="date", rows=rows, selected_date=selected,
        present=present_count, total=len(students),
        today=date.today().isoformat(),
        now=datetime.now().strftime("%H:%M:%S")
    )

@app.route("/monthly")
def monthly():
    conn = database.get_connection()
    month = datetime.now().strftime("%Y-%m")
    total_days = conn.execute(
        "SELECT COUNT(DISTINCT date) FROM attendance WHERE date LIKE ?",
        (f"{month}%",)
    ).fetchone()[0] or 1

    import pandas as pd
    df = pd.read_sql_query("""
        SELECT s.student_id, s.name, s.roll_no,
               COUNT(a.id) as days_present
        FROM students s
        LEFT JOIN attendance a 
            ON s.student_id = a.student_id 
            AND a.date LIKE ?
        GROUP BY s.student_id
        ORDER BY s.name
    """, conn, params=(f"{month}%",))
    conn.close()

    df["pct"] = (df["days_present"] / total_days * 100).round(1)
    rows = [(r.student_id, r.name, r.roll_no, r.days_present, r.pct)
            for r in df.itertuples()]

    return render_template_string(HTML,
        page="monthly", rows=rows,
        total_days=total_days, month=month,
        today=date.today().isoformat(),
        now=datetime.now().strftime("%H:%M:%S")
    )

@app.route("/enrolled")
def enrolled():
    conn = database.get_connection()
    rows = conn.execute(
        "SELECT student_id, name, roll_no, created_at FROM students ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    new_today = get_new_enrollments_today()
    return render_template_string(HTML,
        page="enrolled", rows=rows,
        total=len(rows), new_today=new_today,
        today=date.today().isoformat(),
        now=datetime.now().strftime("%H:%M:%S")
    )

def open_browser():
    webbrowser.open("http://localhost:5000")

if __name__ == "__main__":
    threading.Timer(1.5, open_browser).start()
    app.run(debug=False)