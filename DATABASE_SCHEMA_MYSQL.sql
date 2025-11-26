-- ============================================
-- Face Attendance System - MySQL Database Schema
-- ============================================
-- Database: MySQL 5.7+
-- Timezone: IST (Asia/Kolkata, UTC+5:30)
-- Version: 1.5
-- ============================================

-- Create database
CREATE DATABASE IF NOT EXISTS face_attendance 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE face_attendance;

-- ============================================
-- Table: persons
-- Description: Stores registered employees with face encodings
-- ============================================
CREATE TABLE IF NOT EXISTS persons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    employee_code VARCHAR(50) UNIQUE NOT NULL,
    encoding TEXT NOT NULL,  -- JSON array of 128-d face vector
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active TINYINT(1) DEFAULT 1,
    INDEX idx_persons_employee_code (employee_code),
    INDEX idx_persons_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Table: attendance
-- Description: Records all attendance events with location and IP tracking
-- ============================================
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50) DEFAULT 'live_camera',
    status VARCHAR(20) DEFAULT 'present',
    action VARCHAR(20) DEFAULT 'clock_in',  -- clock_in or clock_out
    latitude FLOAT,
    longitude FLOAT,
    ip_address VARCHAR(50),
    clock_in_time DATETIME,
    clock_out_time DATETIME,
    break_in_time DATETIME,
    break_out_time DATETIME,
    INDEX idx_attendance_timestamp (timestamp),
    INDEX idx_attendance_person_id (person_id),
    INDEX idx_attendance_action (action),
    FOREIGN KEY (person_id) REFERENCES persons(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Table: settings
-- Description: Key-value store for system configuration
-- ============================================
CREATE TABLE IF NOT EXISTS settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(50) UNIQUE NOT NULL,
    value VARCHAR(200) NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE INDEX idx_settings_key (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Table: allowed_ips
-- Description: IP address whitelist for access control
-- ============================================
CREATE TABLE IF NOT EXISTS allowed_ips (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(200),
    is_active TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE INDEX idx_allowed_ips_ip_address (ip_address)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Table: holidays
-- Description: Holiday calendar for attendance tracking
-- ============================================
CREATE TABLE IF NOT EXISTS holidays (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    is_weekoff TINYINT(1) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE INDEX idx_holidays_date (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Default Data: Settings
-- ============================================
INSERT IGNORE INTO settings (`key`, value) VALUES
('office_latitude', '23.022797'),
('office_longitude', '72.531968'),
('geofence_radius', '10000');

-- ============================================
-- Default Data: Allowed IPs
-- ============================================
INSERT IGNORE INTO allowed_ips (ip_address, description, is_active) VALUES
('127.0.0.1', 'Localhost', 1),
('::1', 'Localhost IPv6', 1);

-- ============================================
-- Useful Queries
-- ============================================

-- Get today's attendance count
-- SELECT COUNT(*) FROM attendance 
-- WHERE DATE(timestamp) = CURDATE() 
-- AND clock_in_time IS NOT NULL;

-- Get late arrivals today (after 10 AM)
-- SELECT p.name, a.clock_in_time 
-- FROM attendance a 
-- JOIN persons p ON a.person_id = p.id 
-- WHERE DATE(a.timestamp) = CURDATE() 
-- AND HOUR(a.clock_in_time) >= 10;

-- Get absent employees today
-- SELECT p.name, p.employee_code 
-- FROM persons p 
-- WHERE p.is_active = 1 
-- AND p.id NOT IN (
--   SELECT DISTINCT person_id FROM attendance 
--   WHERE DATE(timestamp) = CURDATE() 
--   AND clock_in_time IS NOT NULL
-- );

-- Calculate work duration
-- SELECT 
--   p.name,
--   a.clock_in_time,
--   a.clock_out_time,
--   ROUND(TIMESTAMPDIFF(MINUTE, a.clock_in_time, a.clock_out_time) / 60, 2) as hours_worked
-- FROM attendance a
-- JOIN persons p ON a.person_id = p.id
-- WHERE a.clock_in_time IS NOT NULL 
-- AND a.clock_out_time IS NOT NULL;

-- ============================================
-- Backup Command (run from terminal)
-- ============================================
-- mysqldump -u username -p face_attendance > backup.sql

-- ============================================
-- Restore Command (run from terminal)
-- ============================================
-- mysql -u username -p face_attendance < backup.sql
