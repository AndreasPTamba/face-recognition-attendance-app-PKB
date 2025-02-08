import tkinter as tk
from tkinter import ttk
import cv2
import PIL.Image, PIL.ImageTk  # Required for image processing with OpenCV and Tkinter
import mysql.connector
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from dotenv import load_dotenv
import os
from controllers.VideoCapture import addName
from controllers.FaceRecognition import load_known_faces
import face_recognition
import numpy as np
from datetime import datetime

class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance System")

        # Mendapatkan ukuran layar
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Menentukan ukuran dan posisi jendela
        window_width = ((screen_width // 5) * 4)
        window_height = ((screen_height // 5) * 4)
        
        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2) - 20
        
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        self.padx = (window_width // 20)
        self.pady = (window_height // 20)
        
        # Frame 1(Camera)
        frame1_width = (self.padx * 12)
        frame1_height = (self.pady * 16)
        
        self.frame1 = tk.Canvas(root, bg="#FF0000", width=frame1_width, height=frame1_height)
        self.frame1.place(x=self.padx, y=(self.pady))
        
        button1 = tk.Button(root, text="Add Student", width=30, height=2, command=lambda: self.add_student())
        button1.place(x=(15 * self.padx), y=(1 * self.pady))
        
        button2 = tk.Button(root, text="View Record", width=30, height=2, command=lambda: self.view_record())
        button2.place(x=(15 * self.padx), y=(3 * self.pady))
        
        # button3 = tk.Button(root, text="Admin", width=30, height=2)
        # button3.place(x=(15 * self.padx), y=(5 * self.pady))
        
        self.cam = cv2.VideoCapture(0)  # Open the camera
        self.known_face_encodings = []
        self.known_face_names = []
        # Load known faces from the dataset
        dataset_path = './dataset'
        load_known_faces(dataset_path, self.known_face_encodings, self.known_face_names)

        # Update canvas with video feed
        self.update_camera()

        # Load environment variables
        load_dotenv()

        # Connect to MySQL database
        self.connect_to_db()
        
    def update_camera(self): 
        ret, frame = self.cam.read()
        if ret:
            # Mengubah frame dari BGR (OpenCV format) ke RGB (face_recognition format)
            imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
            rgb_frame = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            # Deteksi wajah dalam frame
            face_locations = face_recognition.face_locations(rgb_frame)

            if face_locations:
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)


                face_names = []
                for face_encoding, face_location in zip(face_encodings, face_locations):
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    name = "Unknown"

                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    
                    print(f"Face distances: {face_distances}")
                    threshold = 0.46
                    if matches[best_match_index] and face_distances[best_match_index] < threshold:
                        name = self.known_face_names[best_match_index].upper()

                    y1, x2, y2, x1 = face_location
                    y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 2)
                

                    if name not in face_names:
                        face_names.append(name)
                        

                        db_connection = self.connect_to_db()
                        if db_connection:
                            cursor = db_connection.cursor()

                            # Get current date in YYYY-MM-DD format
                            current_date = datetime.now().strftime('%Y-%m-%d')
                            result = None
                            
                            try:
                                if name != "Unknown":
                                    query = "SELECT user_id FROM attendance_records WHERE attendance_date = %s AND user_id = %s"
                                    cursor.execute(query, (current_date, name))
                                    result = cursor.fetchall()

                                if not result and name != "Unknown":
                                    query = "INSERT INTO attendance_records (user_id, attendance_date, attendance_time, attendance_status) VALUES (%s, %s, %s, %s)"
                                    data = (name, current_date, datetime.now().strftime('%H:%M:%S'), 'Present')
                                    cursor.execute(query, data)
                                    db_connection.commit()
                                    print("Data inserted successfully")

                            except mysql.connector.Error as error:
                                print("Failed to fetch data from MySQL table:", error)
                            finally:
                                cursor.close()
                                db_connection.close()
                                print("MySQL connection is closed")

            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Resize image to fit canvas
            resized = cv2.resize(rgb_image, (self.frame1.winfo_width(), self.frame1.winfo_height()))

            # Convert image to PIL format
            img = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(resized))

            # Update canvas with new image
            self.frame1.create_image(0, 0, anchor=tk.NW, image=img)
            self.frame1.image = img  # Keep reference to prevent garbage collection

            # Schedule the next update in 10 milliseconds
            self.root.after(10, self.update_camera)
        
    def view_record(self):
        # Fungsi untuk menampilkan tabel data
        
        # Hentikan pembaruan kamera
        self.root.after_cancel(self.update_camera)

        # Ambil data dari database
        data = self.get_data()

        # Buat tabel untuk menampilkan data
        tree = ttk.Treeview(self.root)
        tree["columns"] = ("nim", "name", "attendance_date", "attendance_time", "attendance_status")

        tree.heading("#0", text="No")
        tree.column("#0",minwidth=0,width=self.padx)
        
        tree.heading("nim", text="NIM")
        tree.column("nim",minwidth=0,width=2 * self.padx)

        tree.heading("name", text="Name")
        tree.column("name",minwidth=0,width=3 * self.padx)

        tree.heading("attendance_date", text="Date")
        tree.column("attendance_date",minwidth=0,width=2 * self.padx)

        tree.heading("attendance_time", text="Time")
        tree.column("attendance_time",minwidth=0,width=2 * self.padx)

        tree.heading("attendance_status", text="Status")
        tree.column("attendance_status",minwidth=0,width=2 * self.padx)


        # Insert data into table
        if data:
            for i, row in enumerate(data, start=1):
                tree.insert("", "end", text=str(i), values=row)
                
        # Place the table in the window
        tree.place(x=self.padx, y=self.pady)
        
            
    def connect_to_db(self):
        try:
            connection = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME")
            )
            print("Connected to MySQL database")
            return connection
        except mysql.connector.Error as error:
            print("Error connecting to MySQL database:", error)
            return None
        
    def get_data(self):
        db_connection = self.connect_to_db()
        if db_connection:
            cursor = db_connection.cursor()

            # Query untuk mengambil data dari dua tabel dan melakukan JOIN
            query = """
                SELECT m.nim, m.name, a.attendance_date, a.attendance_time, a.attendance_status
                FROM mahasiswa m
                RIGHT JOIN attendance_records a ON m.nim = a.user_id
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            db_connection.close()
            return rows
        else:
            return None
        

    def add_student(self):
        # Fungsi untuk menambahkan data mahasiswa ke database

        # Hentikan pembaruan kamera
        self.root.after_cancel(self.update_camera)

        # Buat jendela tambahan
        self.add_student_window = tk.Toplevel(self.root)
        self.add_student_window.title("Add Student")
        
        # Tentukan ukuran dan posisi jendela tambahan
         # Mendapatkan ukuran layar
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Menentukan ukuran dan posisi jendela
        window_width = ((screen_width // 5) * 4)
        window_height = ((screen_height // 5) * 4)
        
        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2) - 20
        
        self.add_student_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        # Sembunyikan jendela utama
        self.root.withdraw()
        self.cam.release()

        # Buat label dan entry untuk NIM
        label_nim = tk.Label(self.add_student_window, text="NIM")
        label_nim.place(x=20, y=20)
        self.entry_nim = tk.Entry(self.add_student_window)
        self.entry_nim.place(x=150, y=20)
        
        # Buat label dan entry untuk nama
        label_name = tk.Label(self.add_student_window, text="Name")
        label_name.place(x=20, y=60)
        self.entry_name = tk.Entry(self.add_student_window)
        self.entry_name.place(x=150, y=60)

        # Buat label dan entry untuk gender
        label_gender = tk.Label(self.add_student_window, text="Gender")
        label_gender.place(x=20, y=100)
        self.selected_option = tk.StringVar()
        options = ["Male", "Female"]
        self.entry_gender = ttk.OptionMenu(self.add_student_window, self.selected_option, options[0], *options)
        self.entry_gender.place(x=150, y=100)

        # Buat label dan entry untuk address
        label_address = tk.Label(self.add_student_window, text="Address")
        label_address.place(x=20, y=140)
        self.entry_address = tk.Entry(self.add_student_window)
        self.entry_address.place(x=150, y=140)

        # Buat label dan entry untuk phone number
        label_phone = tk.Label(self.add_student_window, text="Phone")
        label_phone.place(x=20, y=180)
        self.entry_phone = tk.Entry(self.add_student_window)
        self.entry_phone.place(x=150, y=180)

        # Buat label dan entry untuk email
        label_email = tk.Label(self.add_student_window, text="Email")
        label_email.place(x=20, y=220)
        self.entry_email = tk.Entry(self.add_student_window)
        self.entry_email.place(x=150, y=220)
        
        # Buat tombol untuk membatalkan penambahan data
        button_cancel = tk.Button(self.add_student_window, text="Cancel", command=lambda: self.cancel_add_student())
        button_cancel.place(x=50, y=260)
        # Buat tombol untuk menyimpan data
        button_save = tk.Button(self.add_student_window, text="Save", command=lambda: self.run_add_student_images())
        button_save.place(x=150, y=260)
    
    def save_student(self):
        # Fungsi untuk menyimpan data mahasiswa ke database
        db_connection = self.connect_to_db()
        if db_connection:
            cursor = db_connection.cursor()

            try:
                # Ambil data dari entry
                nim = self.entry_nim.get()
                name = self.entry_name.get()
                gender = self.selected_option.get()
                address = self.entry_address.get()
                phone = self.entry_phone.get()
                email = self.entry_email.get()
                data_path = './dataset/{}'.format(nim)

                query = """
                INSERT INTO mahasiswa (nim, name, gender, address, phone_number, email_address, data_path) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                data = (nim, name, gender, address, phone, email, data_path)
                cursor.execute(query, data)
                db_connection.commit()
                print("Data inserted successfully")

            except mysql.connector.Error as error:
                print("Failed to insert data into MySQL table:", error)
            finally:
                cursor.close()
                db_connection.close()
                print("MySQL connection is closed")
    
    def run_add_student_images(self):
        nim = self.entry_nim.get()
        db_connection = self.connect_to_db()
        if db_connection:
            cursor = db_connection.cursor()
            try:
                query = "SELECT * FROM mahasiswa WHERE nim = %s"
                cursor.execute(query, (nim,))
                result = cursor.fetchone()

                if result:
                    messagebox.showinfo("Warning", f"NIM {nim} exists in the database.")
                else:
                    addName(nim)
                    self.cam = cv2.VideoCapture(0)
                    self.save_student()
                    self.add_student_window.destroy()
                    self.root.deiconify()
                    self.update_camera()
                    
                    
                    
            except mysql.connector.Error as error:
                print("Error validating NIM:", error)
                messagebox.showerror("Error", f"Error validating NIM: {error}")
            finally:
                cursor.close()
                db_connection.close()
                print("MySQL connection is closed")
        
    def cancel_add_student(self):
        # Fungsi untuk membatalkan penambahan data
        self.cam = cv2.VideoCapture(0)
        self.add_student_window.destroy()
        self.root.deiconify()
        self.update_camera()
        
        
        


