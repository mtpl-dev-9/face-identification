-- Complete Database Schema for Face Attendance System
-- Run this file to create all required tables
USE mtpl_website;
-- Leave Types Table
CREATE TABLE IF NOT EXISTS mtpl_leave_types (
    leaveTypeId INT AUTO_INCREMENT PRIMARY KEY,
    leaveTypeName VARCHAR(50) UNIQUE NOT NULL,
    leaveTypeIsPaid TINYINT(1) DEFAULT 1,
    leaveT
ypeIsEncashable TINYINT(1) DEFAULT 0,
    leaveTypeRequireApproval TINYINT(1) DEFAULT 1,
    leaveTypeRequireAttachment TINYINT(1) DEFAULT 0,
    leaveTypeIsActive TINYINT(1) DEFAULT 1,
    leaveTypeCreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Leave Allotment Table
CREATE TABLE IF NOT EXISTS mtpl_leave_allotment (
    allotmentId INT AUTO_INCREMENT PRIMARY KEY,
    allotmentUserId INT NOT NULL,
    allotmentLeaveTypeId INT NOT NULL,
    allotmentTotal DECIMAL(5, 1) NOT NULL DEFAULT 0,
    allotmentYear INT NOT NULL,
    allotmentAssignedBy INT,
    allotmentAssignedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    allotmentUpdatedAt DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_leave_year (allotmentUserId, allotmentLeaveTypeId, allotmentYear),
    INDEX idx_user_year (allotmentUserId, allotmentYear),
    FOREIGN KEY (allotmentLeaveTypeId) REFERENCES mtpl_leave_types(leaveTypeId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Monthly Reports Table
CREATE TABLE IF NOT EXISTS mtpl_monthly_reports (
    reportId INT AUTO_INCREMENT PRIMARY KEY,
    reportUserId INT NOT NULL,
    reportMonth INT NOT NULL,
    reportYear INT NOT NULL,
    reportTotalWorkingHours DECIMAL(10, 2) DEFAULT 0,
    reportWorkedDays INT DEFAULT 0,
    reportTotalWeeklyOff INT DEFAULT 0,
    reportHolidays INT DEFAULT 0,
    reportLeavesTaken DECIMAL(5, 1) DEFAULT 0,
    reportOnTimeEntries INT DEFAULT 0,
    reportEarlyOut INT DEFAULT 0,
    reportLateIn INT DEFAULT 0,
    reportAbsentDays INT DEFAULT 0,
    reportGeneratedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    reportUpdatedAt DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_month_year (reportUserId, reportMonth, reportYear),
    INDEX idx_user_year (reportUserId, reportYear)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create mtpl_users table if it doesn't exist
CREATE TABLE IF NOT EXISTS mtpl_users (
    userId INT AUTO_INCREMENT PRIMARY KEY,
    userFirstName VARCHAR(100) NOT NULL,
    userLastName VARCHAR(100) NOT NULL,
    userEmployeeCode VARCHAR(50) UNIQUE NOT NULL,
    userEmail VARCHAR(150),
    userPhone VARCHAR(20),
    userIsActive VARCHAR(1) DEFAULT '1',
    userCreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_employee_code (userEmployeeCode),
    INDEX idx_user_is_active (userIsActive)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert sample users for testing (optional)
INSERT IGNORE INTO mtpl_users (userFirstName, userLastName, userEmployeeCode, userEmail, userIsActive) VALUES
('John', 'Doe', 'EMP001', 'john.doe@example.com', '1'),
('Jane', 'Smith', 'EMP002', 'jane.smith@example.com', '1'),
('Bob', 'Johnson', 'EMP003', 'bob.johnson@example.com', '1');

SELECT 'mtpl_users table created successfully!' as Status;

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
-- Leave Allotment Table Schema
-- This table stores leave allocations for users

-- Sample data (optional)
-- INSERT INTO mtpl_leave_allotment (allotmentUserId, allotmentLeaveTypeId, allotmentTotal, allotmentYear, allotmentAssignedBy)
-- VALUES (1, 1, 4, 2024, 1), (1, 2, 7, 2024, 1), (1, 3, 0.5, 2024, 1);
CREATE TABLE IF NOT EXISTS `mtpl_leave_allotment` (
  `allotmentId` INT NOT NULL AUTO_INCREMENT,
  `allotmentUserId` INT NOT NULL,
  `allotmentLeaveTypeId` INT NOT NULL,
  `allotmentTotal` DECIMAL(5,1) NOT NULL DEFAULT 0,
  `allotmentYear` INT NOT NULL,
  `allotmentAssignedBy` INT DEFAULT NULL,
  `allotmentAssignedAt` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `allotmentUpdatedAt` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`allotmentId`),
  KEY `idx_user_year` (`allotmentUserId`, `allotmentYear`),
  KEY `idx_leave_type` (`allotmentLeaveTypeId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Check if table was created
SHOW TABLES LIKE 'mtpl_leave_allotment';

-- Show table structure
DESCRIBE mtpl_leave_allotment;

-- Insert sample data
INSERT INTO mtpl_leave_allotment (allotmentUserId, allotmentLeaveTypeId, allotmentTotal, allotmentYear, allotmentAssignedBy)
VALUES 
(1, 1, 4.0, 2024, 1),
(1, 2, 7.0, 2024, 1),
(1, 3, 0.5, 2024, 1);

-- Verify data
SELECT * FROM mtpl_leave_allotment;

INSERT INTO mtpl_users (userId, userFirstName, userLastName, userLogin, userIsActive)
SELECT 
    b.biometricUserId,
    CONCAT('User ', b.biometricUserId) as userFirstName,
    '' as userLastName,
    CONCAT('EMP', LPAD(b.biometricUserId, 4, '0')) as userLogin,
    '1' as userIsActive
FROM mtpl_biometric b
WHERE NOT EXISTS (
    SELECT 1 FROM mtpl_users u WHERE u.userId = b.biometricUserId
)
AND b.biometricIsActive = 1;

-- Verify the fix
SELECT 
    b.biometricId,
    b.biometricUserId,
    u.userFirstName,
    u.userLastName,
    u.userLogin,
    b.biometricCreatedAt
FROM mtpl_biometric b
LEFT JOIN mtpl_users u ON b.biometricUserId = u.userId
WHERE b.biometricIsActive = 1
ORDER BY b.biometricId;

-- Leave Allotment Table Schema
-- This table stores leave allocations for users

-- Sample data (optional)
-- INSERT INTO mtpl_leave_allotment (allotmentUserId, allotmentLeaveTypeId, allotmentTotal, allotmentYear, allotmentAssignedBy)
-- VALUES (1, 1, 4, 2024, 1), (1, 2, 7, 2024, 1), (1, 3, 0.5, 2024, 1);

-- Leave Management System Database Schema
-- Add these tables to your existing mtpl_website database

-- Table: Leave Types (Casual, Sick, Celebratory, etc.)
CREATE TABLE IF NOT EXISTS `mtpl_leave_types` (
  `leaveTypeId` INT AUTO_INCREMENT PRIMARY KEY,
  `leaveTypeName` VARCHAR(50) NOT NULL UNIQUE,
  `leaveTypeIsActive` BOOLEAN DEFAULT TRUE,
  `leaveTypeCreatedAt` DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_active (`leaveTypeIsActive`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: User Leave Balance
CREATE TABLE IF NOT EXISTS `mtpl_user_leave_balance` (
  `balanceId` INT AUTO_INCREMENT PRIMARY KEY,
  `balanceUserId` INT NOT NULL,
  `balanceLeaveTypeId` INT NOT NULL,
  `balanceTotal` INT DEFAULT 0,
  `balanceUsed` INT DEFAULT 0,
  `balanceYear` INT NOT NULL,
  `balanceUpdatedAt` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`balanceLeaveTypeId`) REFERENCES `mtpl_leave_types`(`leaveTypeId`) ON DELETE CASCADE,
  INDEX idx_user_year (`balanceUserId`, `balanceYear`),
  UNIQUE KEY unique_user_leave_year (`balanceUserId`, `balanceLeaveTypeId`, `balanceYear`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: Leave Requests
CREATE TABLE IF NOT EXISTS `mtpl_leave_requests` (
  `leaveRequestId` INT AUTO_INCREMENT PRIMARY KEY,
  `leaveRequestUserId` INT NOT NULL,
  `leaveRequestLeaveTypeId` INT NOT NULL,
  `leaveRequestFromDate` DATE NOT NULL,
  `leaveRequestToDate` DATE NOT NULL,
  `leaveRequestDays` INT NOT NULL,
  `leaveRequestReason` TEXT,
  `leaveRequestStatus` VARCHAR(20) DEFAULT 'pending',
  `leaveRequestApprovedBy` INT,
  `leaveRequestApprovedAt` DATETIME,
  `leaveRequestCreatedAt` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`leaveRequestLeaveTypeId`) REFERENCES `mtpl_leave_types`(`leaveTypeId`) ON DELETE CASCADE,
  INDEX idx_user (`leaveRequestUserId`),
  INDEX idx_status (`leaveRequestStatus`),
  INDEX idx_dates (`leaveRequestFromDate`, `leaveRequestToDate`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert default leave types
INSERT INTO `mtpl_leave_types` (`leaveTypeName`) VALUES
('Casual Leave'),
('Sick Leave'),
('Celebratory Leave'),
('Earned Leave'),
('Maternity Leave'),
('Paternity Leave')
ON DUPLICATE KEY UPDATE `leaveTypeName` = VALUES(`leaveTypeName`);

-- Sample: Assign leave balance to users (Update user IDs as needed)
-- Example: Give user ID 1 -> 12 Casual Leaves, 10 Sick Leaves for 2024
-- INSERT INTO `mtpl_user_leave_balance` (`balanceUserId`, `balanceLeaveTypeId`, `balanceTotal`, `balanceYear`)
-- SELECT 1, leaveTypeId, 12, 2024 FROM `mtpl_leave_types` WHERE `leaveTypeName` = 'Casual Leave'
-- ON DUPLICATE KEY UPDATE `balanceTotal` = VALUES(`balanceTotal`);
-- Multi-Level Approval System Schema

-- Table to store who can approve leave requests
CREATE TABLE IF NOT EXISTS `mtpl_leave_approvers` (
  `approverId` INT NOT NULL AUTO_INCREMENT,
  `approverUserId` INT NOT NULL,
  `approverName` VARCHAR(100) NOT NULL,
  `approverRole` VARCHAR(50) DEFAULT 'Manager',
  `approverIsActive` TINYINT(1) DEFAULT 1,
  `approverCreatedAt` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`approverId`),
  KEY `idx_approver_user` (`approverUserId`),
  UNIQUE KEY `unique_user_role` (`approverUserId`, `approverRole`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table to store approval workflow for each leave request
CREATE TABLE IF NOT EXISTS `mtpl_leave_approvals` (
  `approvalId` INT NOT NULL AUTO_INCREMENT,
  `approvalLeaveRequestId` INT NOT NULL,
  `approvalApproverId` INT NOT NULL,
  `approvalStatus` ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
  `approvalComments` TEXT,
  `approvalApprovedAt` DATETIME NULL,
  `approvalCreatedAt` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`approvalId`),
  KEY `idx_leave_request` (`approvalLeaveRequestId`),
  KEY `idx_approver` (`approvalApproverId`),
  UNIQUE KEY `unique_request_approver` (`approvalLeaveRequestId`, `approvalApproverId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Update leave requests table to add overall status
ALTER TABLE `mtpl_leave_requests` 
ADD COLUMN `leaveRequestOverallStatus` ENUM('pending', 'partial_approved', 'fully_approved', 'rejected') DEFAULT 'pending' AFTER `leaveRequestStatus`;

-- Insert sample approvers
INSERT INTO mtpl_leave_approvers (approverUserId, approverName, approverRole) VALUES
(1, 'Admin User', 'Admin'),
(2, 'HR Manager', 'HR'),
(3, 'Department Manager', 'Manager');

-- User Approvers System - Assign approvers to users, not requests

-- Table to store which approvers are assigned to each user
CREATE TABLE IF NOT EXISTS `mtpl_user_approvers` (
  `userApproverId` INT NOT NULL AUTO_INCREMENT,
  `userApproverUserId` INT NOT NULL,
  `userApproverApproverId` INT NOT NULL,
  `userApproverIsActive` TINYINT(1) DEFAULT 1,
  `userApproverCreatedAt` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`userApproverId`),
  KEY `idx_user` (`userApproverUserId`),
  KEY `idx_approver` (`userApproverApproverId`),
  UNIQUE KEY `unique_user_approver` (`userApproverUserId`, `userApproverApproverId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sample data: Assign approvers to users
INSERT IGNORE INTO mtpl_user_approvers (userApproverUserId, userApproverApproverId) VALUES
(1, 8), (1, 9), (1, 10),  -- User 1 has Admin, HR, Manager approvers
(4, 8), (4, 9),           -- User 4 has Admin, HR approvers
(5, 9), (5, 10);          -- User 5 has HR, Manager approvers

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

-- update the mtpl_option to the total working hours
INSERT INTO mtpl_options (optionKey, optionValue) VALUES ('standard_working_hours', '9');

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
