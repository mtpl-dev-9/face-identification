-- Check which table has data
USE mtpl_website;

SELECT 'mtpl_working_records' as table_name, COUNT(*) as record_count FROM mtpl_working_records
UNION ALL
SELECT 'mtpl_working_reports' as table_name, COUNT(*) as record_count FROM mtpl_working_reports;
