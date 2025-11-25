-- ============================================
-- Face Attendance System - Database Schema
-- ============================================
-- Database: SQLite
-- Timezone: IST (Asia/Kolkata, UTC+5:30)
-- Version: 1.5
-- ============================================

-- ============================================
-- Table: persons
-- Description: Stores registered employees with face encodings
-- ============================================
CREATE TABLE IF NOT EXISTS persons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(120) NOT NULL,
    employee_code VARCHAR(50) UNIQUE NOT NULL,
    encoding TEXT NOT NULL,  -- JSON array of 128-d face vector
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- Index for fast employee code lookup
CREATE UNIQUE INDEX IF NOT EXISTS idx_persons_employee_code 
ON persons(employee_code);

-- ============================================
-- Table: attendance
-- Description: Records all attendance events with location and IP tracking
-- ============================================
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50) DEFAULT 'live_camera',
    status VARCHAR(20) DEFAULT 'present',
    action VARCHAR(20) DEFAULT 'clock_in',  -- clock_in or clock_out
    latitude FLOAT,
    longitude FLOAT,
    ip_address VARCHAR(50),
    clock_in_time DATETIME,
    clock_out_time DATETIME,
    FOREIGN KEY (person_id) REFERENCES persons(id)
);

-- Index for date range queries
CREATE INDEX IF NOT EXISTS idx_attendance_timestamp 
ON attendance(timestamp);

-- Index for person lookup
CREATE INDEX IF NOT EXISTS idx_attendance_person_id 
ON attendance(person_id);

-- ============================================
-- Table: settings
-- Description: Key-value store for system configuration
-- ============================================
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key VARCHAR(50) UNIQUE NOT NULL,
    value VARCHAR(200) NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast settings lookup
CREATE UNIQUE INDEX IF NOT EXISTS idx_settings_key 
ON settings(key);

-- ============================================
-- Table: allowed_ips
-- Description: IP address whitelist for access control
-- ============================================
CREATE TABLE IF NOT EXISTS allowed_ips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(200),
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast IP validation
CREATE UNIQUE INDEX IF NOT EXISTS idx_allowed_ips_ip_address 
ON allowed_ips(ip_address);

-- ============================================
-- Default Data: Settings
-- ============================================
INSERT OR IGNORE INTO settings (key, value) VALUES
('office_latitude', '23.022797'),
('office_longitude', '72.531968'),
('geofence_radius', '10000');

-- ============================================
-- Default Data: Allowed IPs
-- ============================================
INSERT OR IGNORE INTO allowed_ips (ip_address, description, is_active) VALUES
('127.0.0.1', 'Localhost', 1),
('::1', 'Localhost IPv6', 1);

-- ============================================
-- Sample Data (for testing)
-- ============================================

-- Sample Person
-- INSERT INTO persons (name, employee_code, encoding, is_active) VALUES
-- ('John Doe', 'EMP001', '[-0.123, 0.456, -0.789, ...]', 1);

-- Sample Attendance (Clock In)
-- INSERT INTO attendance (person_id, action, latitude, longitude, ip_address, clock_in_time) VALUES
-- (1, 'clock_in', 23.022797, 72.531968, '192.168.1.100', '2024-01-15 09:30:00');

-- Sample Attendance (Clock Out - update existing record)
-- UPDATE attendance 
-- SET clock_out_time = '2024-01-15 18:30:00', action = 'clock_out'
-- WHERE id = 1;

-- ============================================
-- Useful Queries
-- ============================================

-- Get today's attendance count
-- SELECT COUNT(*) FROM attendance 
-- WHERE DATE(timestamp) = DATE('now', 'localtime') 
-- AND clock_in_time IS NOT NULL;

-- Get late arrivals today (after 10 AM)
-- SELECT p.name, a.clock_in_time 
-- FROM attendance a 
-- JOIN persons p ON a.person_id = p.id 
-- WHERE DATE(a.timestamp) = DATE('now', 'localtime') 
-- AND CAST(strftime('%H', a.clock_in_time) AS INTEGER) >= 10;

-- Get absent employees today
-- SELECT p.name, p.employee_code 
-- FROM persons p 
-- WHERE p.is_active = 1 
-- AND p.id NOT IN (
--   SELECT DISTINCT person_id FROM attendance 
--   WHERE DATE(timestamp) = DATE('now', 'localtime') 
--   AND clock_in_time IS NOT NULL
-- );

-- Calculate work duration
-- SELECT 
--   p.name,
--   a.clock_in_time,
--   a.clock_out_time,
--   ROUND((julianday(a.clock_out_time) - julianday(a.clock_in_time)) * 24, 2) as hours_worked
-- FROM attendance a
-- JOIN persons p ON a.person_id = p.id
-- WHERE a.clock_in_time IS NOT NULL 
-- AND a.clock_out_time IS NOT NULL;

-- ============================================
-- Maintenance Commands
-- ============================================

-- Optimize database
-- VACUUM;

-- Analyze for query optimization
-- ANALYZE;

-- Check database integrity
-- PRAGMA integrity_check;

-- Get database size
-- SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size();

-- ============================================
-- Backup Command (run from terminal)
-- ============================================
-- sqlite3 instance/attendance.db .dump > backup.sql

-- ============================================
-- Restore Command (run from terminal)
-- ============================================
-- sqlite3 instance/attendance.db < backup.sql
