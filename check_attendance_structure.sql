-- Check attendance table structure
USE mtpl_website;

DESCRIBE mtpl_attendance;

-- Check actual data types
SELECT 
    attendanceUserId,
    attendanceTimestamp,
    attendanceClockInTime,
    attendanceClockOutTime,
    TIME(attendanceClockInTime) as clock_in_time_only,
    TIME(attendanceClockOutTime) as clock_out_time_only
FROM mtpl_attendance 
WHERE attendanceUserId = 1
ORDER BY attendanceTimestamp DESC 
LIMIT 3;
