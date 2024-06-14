import tkinter as tk
from tkinter import ttk
import cv2
import PIL.Image, PIL.ImageTk  # Required for image processing with OpenCV and Tkinter
import mysql.connector
from tkinter import *
from tkinter import ttk

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
        
        button1 = tk.Button(root, text="Admin", width=30, height=2)
        button1.place(x=(15 * self.padx), y=(1 * self.pady))
        
        button2 = tk.Button(root, text="Admin 2", width=30, height=2, command=lambda: self.view_record())
        button2.place(x=(15 * self.padx), y=(3 * self.pady))
        
        button3 = tk.Button(root, text="Admin", width=30, height=2)
        button3.place(x=(15 * self.padx), y=(5 * self.pady))
        
        # Initialize OpenCV video capture
        self.cap = cv2.VideoCapture(0)  # Assuming the default camera (index 0)

        # Update canvas with video feed
        self.update_camera()
        
        self.connect_to_db()
        
    def update_camera(self):
        
        ret, frame = self.cap.read()  # Read frame from the camera

        if ret:
            # Convert OpenCV BGR format to RGB format compatible with Tkinter
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
                host="localhost",
                user="root",
                database="face_recognition_attendance"
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
                LEFT JOIN attendance_records a ON m.nim = a.user_id
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            db_connection.close()
            return rows
        else:
            return None
        

if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()
