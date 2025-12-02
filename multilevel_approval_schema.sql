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