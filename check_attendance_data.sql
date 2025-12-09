-- Check if there's attendance data
USE mtpl_website;

-- Check attendance records
SELECT COUNT(*) as attendance_count FROM mtpl_attendance;

-- Check manual time entries
SELECT COUNT(*) as manual_entries_count FROM mtpl_manual_time_entries;

-- Check working reports
SELECT COUNT(*) as working_reports_count FROM mtpl_working_reports;

-- Show sample attendance data
SELECT attendanceUserId, DATE(attendanceTimestamp) as date, attendanceClockInTime, attendanceClockOutTime 
FROM mtpl_attendance 
ORDER BY attendanceTimestamp DESC 
LIMIT 5;
