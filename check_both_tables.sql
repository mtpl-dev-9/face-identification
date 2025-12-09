-- Check which working table exists
USE mtpl_website;

-- Check for mtpl_working_records
SELECT 'mtpl_working_records' as table_name, COUNT(*) as exists_count 
FROM information_schema.tables 
WHERE table_schema = 'mtpl_website' AND table_name = 'mtpl_working_records'
UNION ALL
-- Check for mtpl_working_reports
SELECT 'mtpl_working_reports' as table_name, COUNT(*) as exists_count 
FROM information_schema.tables 
WHERE table_schema = 'mtpl_website' AND table_name = 'mtpl_working_reports';
