This README file provides instructions on how to set up and run the face-recognition-attendance-app-pkb application.

# face-attendace-app-PKB

Final Project PKB Universitas Udayana

This application is a face recognition attendance system built with Python, Tkinter, OpenCV, face-recognition library, and MySQL.

## Database Query

To set up the database, execute the following SQL queries:

```bash
CREATE DATABASE face_recognition_attendance;

CREATE TABLE mahasiswa (
    nim VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255),
    gender VARCHAR(10),
    address VARCHAR(255),
    phone_number VARCHAR(20),
    email_address VARCHAR(255),
    data_path VARCHAR(255)
);

CREATE TABLE attendance_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(20),
    attendance_date DATE,
    attendance_time TIME,
    attendance_status VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES mahasiswa(nim)
);
```

## How to Run the Application

Follow these steps to get the application running on your local machine.

### Prerequisites

Before you begin, ensure you have the following installed:

* **Python 3.x**: The application is developed with Python.
* **MySQL Database**: You need a running MySQL server for the database.
* **Webcam**: A functional webcam is required for face recognition and capturing new student images.

### Installation

1.  **Clone the Repository (if applicable):** If you haven't already, clone the repository to your local machine.

2.  **Create a Virtual Environment (Recommended):**
    Navigate to the project directory in your terminal and create a virtual environment:

    ```bash
    python -m venv venv
    ```

3.  **Activate the Virtual Environment:**

    * **Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    * **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  **Install Dependencies:**
    Install the required Python libraries using pip. These include `tkinter`, `opencv-python`, `Pillow`, `mysql-connector-python`, `face_recognition`, and `python-dotenv`.

    ```bash
    pip install opencv-python Pillow mysql-connector-python face-recognition python-dotenv
    ```

### Database Configuration

1.  **Set up MySQL Database:**
    Ensure your MySQL server is running. Create the `face_recognition_attendance` database and the `mahasiswa` and `attendance_records` tables using the SQL queries provided in the "Database Query" section above.

2.  **Create a `.env` file:**
    In the root directory of your project, create a file named `.env` (note the leading dot). This file will store your database credentials. Add the following lines, replacing the placeholder values with your actual MySQL database credentials:

    ```
    DB_HOST=localhost
    DB_USER=your_mysql_username
    DB_PASSWORD=your_mysql_password
    DB_NAME=face_recognition_attendance
    ```
    The `.env` file is included in the `.gitignore` to prevent sensitive information from being committed to version control.

### Running the Application

1.  **Prepare the Dataset Directory:**
    Create a `dataset` folder in the root directory of your project. This folder will store the facial images of known students.

2.  **Launch the Application:**
    With your virtual environment activated, run the main application file:

    ```bash
    python Main.py
    ```

### Adding New Students

To add a new student to the system:

1.  Click the "Add Student" button on the main application window.
2.  A new window will appear where you can enter the student's details (NIM, Name, Gender, Address, Phone, Email).
3.  After filling in the details, click "Save". The application will then activate your webcam to capture 5 images of the student's face, saving them into a new folder within the `dataset` directory, named after their NIM.
4.  The student's details will be saved to the `mahasiswa` table in the database.

### Viewing Attendance Records

To view the attendance records:

1.  Click the "View Record" button on the main application window.
2.  This will display a table showing the attendance records, including NIM, Name, Date, Time, and Status.

---
_Note: The `FaceRecognition.py` module includes debug statements for loading images and face detection, which can be useful for troubleshooting. The `FaceRecognition.py` module also sets a threshold of 0.46 for face matching._
