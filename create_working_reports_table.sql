-- Create mtpl_working_reports table
USE mtpl_website;

CREATE TABLE IF NOT EXISTS mtpl_working_reports (
    recordId INT AUTO_INCREMENT PRIMARY KEY,
    recordUserId INT NOT NULL,
    recordDate DATE NOT NULL,
    recordClockInTime TIME NULL,
    recordClockOutTime TIME NULL,
    recordWorkedHours DECIMAL(10, 2) NULL,
    recordTotalHoursDifference DECIMAL(10, 2) NULL,
    recordCreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    recordUpdatedAt DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (recordUserId),
    INDEX idx_date (recordDate)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
