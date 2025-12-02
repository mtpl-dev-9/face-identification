-- Run this in MySQL Workbench if table doesn't exist

USE mtpl_website;

-- Create the leave allotment table
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