-- Add reportLeaveDetails column to mtpl_monthly_reports table
ALTER TABLE mtpl_monthly_reports 
ADD COLUMN reportLeaveDetails TEXT NULL AFTER reportLeavesTaken;
