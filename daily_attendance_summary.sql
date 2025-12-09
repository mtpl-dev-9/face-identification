-- Daily Attendance Summary Table
CREATE TABLE IF NOT EXISTS mtpl_daily_attendance_summary (
    summaryId INT AUTO_INCREMENT PRIMARY KEY,
    summaryUserId INT NOT NULL,
    summaryDate DATE NOT NULL,
    summaryClockInTime TIME,
    summaryClockOutTime TIME,
    summaryWorkedHours DECIMAL(5,2) DEFAULT 0.00,
    summaryPendingHours DECIMAL(5,2) DEFAULT 0.00,
    summaryCreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    summaryUpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_date (summaryUserId, summaryDate),
    INDEX idx_user_date (summaryUserId, summaryDate),
    INDEX idx_date (summaryDate)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
