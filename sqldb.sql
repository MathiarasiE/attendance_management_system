-- Create the database
CREATE DATABASE attendance_db;

-- Use the newly created database
USE attendance_db;

-- Create the attendance_records table
CREATE TABLE attendance_records (
    student_id VARCHAR(50) PRIMARY KEY,
    student_name VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    status ENUM('present', 'absent', 'on_duty') NOT NULL
);
select * from attendance_records;