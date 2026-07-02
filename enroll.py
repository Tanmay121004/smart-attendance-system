
import os
import pickle
import cv2
import face_recognition
import database

DATASET_DIR = "dataset"
ENCODINGS_PATH = "encodings/encodings.pickle"
NUM_SAMPLES = 20

def capture_face_images(student_id):
    save_dir = os.path.join(DATASET_DIR, student_id)
    os.makedirs(save_dir, exist_ok=True)

    cam = cv2.VideoCapture(0)
    face_detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    count = 0
    print(f"[INFO] Camera khul rahi hai... {NUM_SAMPLES} photos lenge.")

    while count < NUM_SAMPLES:
        ret, frame = cam.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
        )

        for (x, y, w, h) in faces:
            count += 1
            face_img = frame[y:y+h, x:x+w]
            img_path = os.path.join(save_dir, f"{count}.jpg")
            cv2.imwrite(img_path, face_img)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"Captured: {count}/{NUM_SAMPLES}",
                        (x, y-10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 0), 2)
            break

        cv2.imshow("Enrollment - press q to quit", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cam.release()
    cv2.destroyAllWindows()
    print(f"[INFO] {count} photos capture hui {student_id} ke liye")
    return save_dir

def build_encodings(student_id, image_dir):
    known_encodings = []
    known_ids = []

    if os.path.exists(ENCODINGS_PATH):
        with open(ENCODINGS_PATH, "rb") as f:
            data = pickle.load(f)
            known_encodings = data["encodings"]
            known_ids = data["ids"]

    new_count = 0
    print("[INFO] Face encodings ban rahe hain, thoda wait karo...")

    for filename in os.listdir(image_dir):
        img_path = os.path.join(image_dir, filename)
        image = face_recognition.load_image_file(img_path)
        boxes = face_recognition.face_locations(image, model="hog")
        encodings = face_recognition.face_encodings(image, boxes)

        for enc in encodings:
            known_encodings.append(enc)
            known_ids.append(student_id)
            new_count += 1

    os.makedirs(os.path.dirname(ENCODINGS_PATH), exist_ok=True)
    with open(ENCODINGS_PATH, "wb") as f:
        pickle.dump({"encodings": known_encodings, "ids": known_ids}, f)

    print(f"[INFO] {new_count} encodings save hui {student_id} ke liye")

def main():
    database.init_db()

    student_id = input("Student ID daalo (e.g. roll number): ").strip()
    name = input("Student ka naam daalo: ").strip()
    roll_no = input("Roll No daalo: ").strip()

    print(f"\n[INFO] {name} ka enrollment shuru ho raha hai...")

    image_dir = capture_face_images(student_id)
    build_encodings(student_id, image_dir)
    database.add_student(student_id, name, roll_no)

    print(f"\n[SUCCESS] {name} successfully enrolled!")

if __name__ == "__main__":
    main()