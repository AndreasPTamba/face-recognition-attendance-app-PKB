import face_recognition
import cv2
import os
import numpy as np

# Memuat database wajah (foto wajah dengan nama yang dikenal)

def load_known_faces(dataset_path, known_face_encodings, known_face_names):
    for class_name in os.listdir(dataset_path):
        class_folder = os.path.join(dataset_path, class_name)
        if os.path.isdir(class_folder):
            for file in os.listdir(class_folder):
                if file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.png'):
                    image_path = os.path.join(class_folder, file)
                    print(f"Loading image: {image_path}")  # Debug statement
                    image = face_recognition.load_image_file(image_path)
                    encodings = face_recognition.face_encodings(image)
                    if encodings:
                        encoding = encodings[0]
                        known_face_encodings.append(encoding)
                        known_face_names.append(class_name)
                        print(f"Face found in {image_path}")  # Debug statement
                    else:
                        print(f"No face found in {image_path}")
def faceRecognition():
    known_face_encodings = []
    known_face_names = []
    # Load known faces from the dataset
    dataset_path = './dataset'  # Ganti dengan path ke dataset Anda
    load_known_faces(dataset_path)

    # Inisialisasi video capture
    cam = cv2.VideoCapture(0)

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        # Mengubah frame dari BGR (OpenCV format) ke RGB (face_recognition format)
        imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        rgb_frame = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        # Deteksi wajah dalam frame
        face_locations = face_recognition.face_locations(rgb_frame)

        # Debug statement untuk memeriksa face_locations
        print(f"Face locations: {face_locations}")

        if face_locations:
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            # Debug statement untuk memeriksa face_encodings
            print(f"Face encodings: {face_encodings}")

            face_names = []
            for face_encoding, face_location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index].upper()
                    y1, x2, y2, x1 = face_location
                    y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                
                    if name not in face_names:
                        face_names.append(name)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()