-- Fix leaveRequestDays column to support decimal values (half days)
ALTER TABLE mtpl_leave_requests 
MODIFY COLUMN leaveRequestDays DECIMAL(5,1) NOT NULL;
