-- Add user ID to leave approvals table for better tracking

ALTER TABLE `mtpl_leave_approvals` 
ADD COLUMN `approvalUserId` INT NULL AFTER `approvalApproverId`;

-- Update existing records with user ID from leave requests
UPDATE mtpl_leave_approvals la
JOIN mtpl_leave_requests lr ON la.approvalLeaveRequestId = lr.leaveRequestId
SET la.approvalUserId = lr.leaveRequestUserId;