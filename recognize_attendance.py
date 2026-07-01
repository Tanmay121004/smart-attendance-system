import os
import pickle
import time
import cv2
import face_recognition
import numpy as np
import database

ENCODINGS_PATH = "encodings/encodings.pickle"
MATCH_TOLERANCE = 0.5
BLINK_WINDOW_FRAMES = 15
RESIZE_SCALE = 0.5
class FaceTrack:
    def __init__(self):
        self.eye_history = []
        self.blink_verified = False
        self.last_seen = time.time()

def detect_blink(history):
    if len(history) < 3:
        return False
    
    # consecutive same states hatao
    # [T,T,F,F,T,T] -> [T,F,T]
    collapsed = [history[0]]
    for state in history[1:]:
        if state != collapsed[-1]:
            collapsed.append(state)
    
    # open->closed->open pattern dhundho
    for i in range(len(collapsed) - 2):
        if collapsed[i] == True and collapsed[i+1] == False and collapsed[i+2] == True:
            return True
    return False

def load_encodings():
    if not os.path.exists(ENCODINGS_PATH):
        raise FileNotFoundError(
            "Encodings nahi mili! Pehle enroll.py chalao."
        )
    with open(ENCODINGS_PATH, "rb") as f:
        data = pickle.load(f)
    return data["encodings"], data["ids"]

def main():
    database.init_db()
    known_encodings, known_ids = load_encodings()
    student_lookup = {sid: (name, roll) 
                      for sid, name, roll in database.get_all_students()}

    face_detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    eye_detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_eye.xml"
    )

    cam = cv2.VideoCapture(0)
    tracks = {}

    print("[INFO] Camera shuru ho rahi hai... q dabao band karne ke liye")

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        small = cv2.resize(frame, (0, 0), fx=RESIZE_SCALE, fy=RESIZE_SCALE)
        rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        face_locations = face_recognition.face_locations(rgb_small, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            top, right, bottom, left = [int(v / RESIZE_SCALE) 
                                         for v in (top, right, bottom, left)]

            distances = face_recognition.face_distance(known_encodings, face_encoding)
            student_id = "Unknown"
            if len(distances) > 0:
                best_idx = int(np.argmin(distances))
                if distances[best_idx] <= MATCH_TOLERANCE:
                    student_id = known_ids[best_idx]

            face_roi = gray[max(0,top):bottom, max(0,left):right]
            eyes = eye_detector.detectMultiScale(
                face_roi, scaleFactor=1.1, minNeighbors=5
            )
            eyes_detected = len(eyes) >= 1

            if student_id not in tracks:
                tracks[student_id] = FaceTrack()
            track = tracks[student_id]
            track.last_seen = time.time()
            track.eye_history.append(eyes_detected)
            if len(track.eye_history) > BLINK_WINDOW_FRAMES:
                track.eye_history.pop(0)

            if not track.blink_verified and detect_blink(track.eye_history):
                track.blink_verified = True

            color = (0, 0, 255)
            label = "Unknown"

            if student_id != "Unknown":
                name, roll = student_lookup.get(student_id, (student_id, ""))
                if track.blink_verified:
                    color = (0, 200, 0)
                    label = f"{name} - Verified!"
                    if database.mark_attendance(student_id):
                        print(f"[ATTENDANCE] {name} present mark ho gaya!")
                else:
                    color = (0, 165, 255)
                    label = f"{name} - Blink karo!"

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, label, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        cv2.imshow("Smart Attendance", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
