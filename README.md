# Smart Attendance System using Face Recognition 🎓

A real-time attendance marking system built with Python that uses your webcam to detect and recognize faces — and won't let a printed photo fool it, thanks to **blink-based liveness detection**.

 The idea was simple: why should a teacher manually call out names when a camera can do it in seconds?

---

## What It Does

When you run the system, it opens your webcam and starts looking for faces. If it recognizes someone who's been enrolled, it waits for them to **blink** before marking them present. No blink = no attendance. This one small check makes it surprisingly hard to spoof with a photo or phone screen.

Once attendance is marked, you can open a browser dashboard that shows who's present, who's absent, and the overall percentage — refreshing itself every 10 seconds automatically.

---

## Features

- 👁️ **Blink-based liveness detection** — prevents photo spoofing without needing any extra hardware
- 🧠 **Face recognition** — uses 128-dimensional face encodings to identify enrolled students
- 🗃️ **SQLite database** — stores student records and attendance logs locally, no internet needed
- 📊 **Live web dashboard** — Flask-powered browser UI, auto-refreshes every 10 seconds
- 📁 **CSV report export** — daily and summary reports saved to the `reports/` folder
- 🔁 **Duplicate prevention** — same person can't be marked twice in one day at the database level

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.11 | Core language |
| OpenCV | Webcam capture, Haar cascade face + eye detection |
| face_recognition (dlib) | 128-D face encoding and matching |
| SQLite3 | Local database for students and attendance |
| Flask | Web dashboard backend |
| Pandas | Report generation and CSV export |
| Git + GitHub | Version control |

---

## Project Structure

```
smart_attendance/
├── database.py               # SQLite schema and all DB helper functions
├── enroll.py                 # Capture face images and generate encodings
├── recognize_attendance.py   # Live webcam loop with blink detection
├── generate_report.py        # Daily and summary CSV report generator
├── dashboard.py              # Flask web dashboard
├── test_camera.py            # Quick webcam sanity check
├── dataset/                  # Face images per student (gitignored)
├── encodings/                # Stored face encodings pickle file (gitignored)
├── reports/                  # Generated attendance CSVs (gitignored)
└── attendance.db             # SQLite database (gitignored)
```

---

## How Blink Detection Works

Instead of relying on dlib's 68-point facial landmark model (which requires a large external file download), this project uses OpenCV's built-in eye Haar cascade.

Every frame, the eye cascade runs inside the detected face region. We track whether eyes are visible or not across a rolling window of 15 frames. A genuine blink creates a pattern like this:

```
Eyes Open → Eyes Closed → Eyes Open
  True    →    False    →    True
```

We collapse consecutive identical states and look for exactly that `True → False → True` pattern. A static photo held to the camera will always stay `True` — so it never passes the check.

It's lightweight, needs no external model downloads, and works on a regular laptop CPU in real time.

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/Tanmay121004/smart-attendance-system.git
cd smart-attendance-system
```

### 2. Create virtual environment (Python 3.11 recommended)
```bash
py -3.11 -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies
```bash
pip install opencv-python
pip install cmake
pip install dlib-bin          # Pre-built wheel, no compiler needed
pip install face_recognition --no-deps
pip install face-recognition-models Click Pillow numpy pandas flask
```

> **Note:** `dlib` won't build from source on Python 3.13+. Stick to Python 3.11 for a smooth install. Use `dlib-bin` instead of `dlib` to skip the C++ compilation step entirely.

---

## Usage

### Step 1 — Enroll students (one time per student)
```bash
python enroll.py
```
Enter the student's ID, name, and roll number when prompted. The webcam will open and automatically capture 20 face images, generate encodings, and save everything to the database.

### Step 2 — Take attendance (run daily)
```bash
python recognize_attendance.py
```
The webcam loop starts. Recognized faces show an **orange box** until a blink is detected — then the box turns **green** and attendance is logged. Press `q` to quit.

### Step 3 — View the dashboard
```bash
python dashboard.py
```
Open `http://localhost:5000` in your browser. Shows today's attendance, present/absent count, percentage, and time-in for each student. Auto-refreshes every 10 seconds.

### Step 4 — Generate reports
```bash
python generate_report.py              # today's report
python generate_report.py 2026-07-01   # specific date
python generate_report.py --summary    # overall % per student
```

---

## Color System in Recognition Window

| Color | Meaning |
|-------|---------|
| 🔴 Red | Face not recognized |
| 🟠 Orange | Recognized — waiting for blink |
| 🟢 Green | Blink verified — attendance marked |

---

## Database Schema

**students table**
```
student_id | name | roll_no | created_at
```

**attendance table**
```
id | student_id | date | time_in | status
UNIQUE constraint on (student_id, date) — prevents duplicate entries
```

---

## Known Limitations

These came up during testing and are worth knowing:

- **Low light performance** — Haar cascades lose accuracy in poor lighting. A CNN-based detector (MTCNN) would handle this better but is slower on CPU.
- **Video replay attack** — a video of someone blinking could still pass the liveness check. Defeating this properly needs depth sensing or randomized challenges.
- **Linear search** — matching is O(n) over all stored encodings. Fine for a class of 60, but would need approximate nearest-neighbor indexing (like FAISS) for larger deployments.
- **Single angle enrollment** — enrolling from one angle only can reduce recognition accuracy. Multi-angle enrollment would improve robustness.

---

## Possible Extensions

- Email or SMS alert for students with attendance below a threshold
- Multi-camera support for larger classrooms
- Admin login for the dashboard
- Export to Excel with conditional formatting
- Deploy Flask on a local network so the dashboard is accessible from any device on the same WiFi

---

## Author

**Tanmay Sinha**  
B.Tech — Electronics and Communication Engineering  
GitHub: [@Tanmay121004](https://github.com/Tanmay121004)

---

## License

MIT License — feel free to use, modify, and build on this.
