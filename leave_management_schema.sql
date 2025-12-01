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
