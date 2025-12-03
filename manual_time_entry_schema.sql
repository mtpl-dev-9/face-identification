-- ============================================
-- Manual Time Entry Table - MySQL Database Schema
-- ============================================
-- Database: MySQL 5.7+
-- Timezone: IST (Asia/Kolkata, UTC+5:30)
-- ============================================

-- ============================================
-- Table: mtpl_manual_time_entries
-- Description: Stores manually entered time entries for users
-- Allows admin to set fixed check-in, check-out, break-in, break-out times and working dates
-- ============================================
CREATE TABLE IF NOT EXISTS mtpl_manual_time_entries (
    entryId INT AUTO_INCREMENT PRIMARY KEY,
    entryUserId INT NOT NULL,
    entryWorkingDate DATE NOT NULL,
    entryCheckInTime TIME NULL,
    entryCheckOutTime TIME NULL,
    entryBreakInTime TIME NULL,
    entryBreakOutTime TIME NULL,
    entryCreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    entryUpdatedAt DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    entryCreatedBy INT NULL COMMENT 'Admin user ID who created this entry',
    INDEX idx_entry_user_id (entryUserId),
    INDEX idx_entry_working_date (entryWorkingDate),
    INDEX idx_entry_user_date (entryUserId, entryWorkingDate),
    UNIQUE KEY unique_user_date (entryUserId, entryWorkingDate),
    FOREIGN KEY (entryUserId) REFERENCES mtpl_users(userId) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

