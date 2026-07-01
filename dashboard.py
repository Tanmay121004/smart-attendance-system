from flask import Flask, render_template_string
from datetime import date
import database

app = Flask(__name__)
database.init_db()

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart Attendance</title>
    <meta http-equiv="refresh" content="10">
    <style>
        body { font-family: Arial; background: #1a1a2e; color: white; padding: 20px; }
        h1 { color: #00d4ff; text-align: center; }
        .stats { display: flex; gap: 20px; justify-content: center; margin: 20px 0; }
        .card { background: #16213e; padding: 20px 40px; border-radius: 10px; text-align: center; }
        .card h2 { font-size: 40px; margin: 0; color: #00d4ff; }
        .card p { margin: 5px 0; color: #aaa; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th { background: #00d4ff; color: #1a1a2e; padding: 12px; }
        td { padding: 12px; border-bottom: 1px solid #333; text-align: center; }
        .present { color: #00ff88; font-weight: bold; }
        .absent { color: #ff4444; font-weight: bold; }
        tr:hover { background: #16213e; }
    </style>
</head>
<body>
    <h1>🎓 Smart Attendance System</h1>
    <div class="stats">
        <div class="card">
            <h2>{{ present }}</h2>
            <p>Present Today</p>
        </div>
        <div class="card">
            <h2>{{ total - present }}</h2>
            <p>Absent Today</p>
        </div>
        <div class="card">
            <h2>{{ "%.0f"|format(present/total*100 if total else 0) }}%</h2>
            <p>Attendance %</p>
        </div>
    </div>
    <h3 style="color:#aaa">📅 Date: {{ today }}</h3>
    <table>
        <tr>
            <th>Roll No</th>
            <th>Name</th>
            <th>Time In</th>
            <th>Status</th>
        </tr>
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
    <p style="color:#555; text-align:center; margin-top:20px">
        Auto refresh: har 10 seconds mein update hoga
    </p>
</body>
</html>
"""

@app.route("/")
def index():
    today = date.today().isoformat()
    rows = database.get_attendance_for_date(today)
    students = database.get_all_students()
    
    present_count = sum(1 for r in rows if r[4] == "Present")
    total = len(students)

    return render_template_string(HTML, 
        rows=rows, 
        today=today,
        present=present_count,
        total=total
    )

if __name__ == "__main__":
    app.run(debug=True)