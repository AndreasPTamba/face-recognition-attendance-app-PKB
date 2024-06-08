# face-attendace-app-PKB
Final Project PKB Universitas Udayana

Database Query

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
