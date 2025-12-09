-- Add day_type column to leave requests table
ALTER TABLE mtpl_leave_requests 
ADD COLUMN leaveRequestDayType VARCHAR(10) DEFAULT 'full';
