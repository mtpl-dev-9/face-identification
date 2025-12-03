-- Add new columns to mtpl_leave_types table
-- Run this to update existing database

ALTER TABLE `mtpl_leave_types` 
ADD COLUMN `leaveTypeIsPaid` TINYINT(1) DEFAULT 1 AFTER `leaveTypeName`,
ADD COLUMN `leaveTypeIsEncashable` TINYINT(1) DEFAULT 0 AFTER `leaveTypeIsPaid`,
ADD COLUMN `leaveTypeRequireApproval` TINYINT(1) DEFAULT 1 AFTER `leaveTypeIsEncashable`,
ADD COLUMN `leaveTypeRequireAttachment` TINYINT(1) DEFAULT 0 AFTER `leaveTypeRequireApproval`;

-- Update existing records to have default values
UPDATE `mtpl_leave_types` 
SET 
  `leaveTypeIsPaid` = 1,
  `leaveTypeIsEncashable` = 0,
  `leaveTypeRequireApproval` = 1,
  `leaveTypeRequireAttachment` = 0
WHERE `leaveTypeIsPaid` IS NULL;
