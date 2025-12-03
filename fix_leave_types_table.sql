-- Run this SQL to add missing columns to mtpl_leave_types table

ALTER TABLE mtpl_leave_types 
ADD COLUMN leaveTypeIsPaid TINYINT(1) DEFAULT 1;

ALTER TABLE mtpl_leave_types 
ADD COLUMN leaveTypeIsEncashable TINYINT(1) DEFAULT 0;

ALTER TABLE mtpl_leave_types 
ADD COLUMN leaveTypeRequireApproval TINYINT(1) DEFAULT 1;

ALTER TABLE mtpl_leave_types 
ADD COLUMN leaveTypeRequireAttachment TINYINT(1) DEFAULT 0;
