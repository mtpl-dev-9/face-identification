-- Check if mtpl_working_reports table exists and show its structure
USE mtpl_website;

SHOW TABLES LIKE 'mtpl_working_reports';

DESCRIBE mtpl_working_reports;

SELECT COUNT(*) as total_records FROM mtpl_working_reports;
