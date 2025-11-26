"""
Script to update all database queries from old schema to MTPL schema
Run this to see all the changes needed in app.py
"""

OLD_TO_NEW_MAPPING = {
    # Person/Biometric
    "Person.query.filter_by(is_active=True)": "Person.query.filter_by(biometricIsActive=True)",
    "Person.query.filter_by(employee_code=": "Person.query.filter_by(biometricUserId=",
    "p.encoding": "p.biometricEncoding",
    "person.encoding": "person.biometricEncoding",
    
    # Attendance
    "Attendance.timestamp": "Attendance.attendanceTimestamp",
    "Attendance.person_id": "Attendance.attendanceUserId",
    "Attendance.clock_in_time": "Attendance.attendanceClockInTime",
    "Attendance.clock_out_time": "Attendance.attendanceClockOutTime",
    "Attendance.break_in_time": "Attendance.attendanceBreakInTime",
    "Attendance.break_out_time": "Attendance.attendanceBreakOutTime",
    "Attendance.action": "Attendance.attendanceAction",
    "Attendance.latitude": "Attendance.attendanceLatitude",
    "Attendance.longitude": "Attendance.attendanceLongitude",
    "Attendance.ip_address": "Attendance.attendanceIpAddress",
    "Attendance.source": "Attendance.attendanceSource",
    "Attendance.status": "Attendance.attendanceStatus",
    
    # Instance properties
    "attendance.person_id": "attendance.attendanceUserId",
    "record.person_id": "record.attendanceUserId",
    "today_record.action": "today_record.attendanceAction",
    "today_record.clock_out_time": "today_record.attendanceClockOutTime",
    "today_record.clock_in_time": "today_record.attendanceClockInTime",
    "today_record.break_in_time": "today_record.attendanceBreakInTime",
    "today_record.break_out_time": "today_record.attendanceBreakOutTime",
    
    # Holiday
    "Holiday.date": "Holiday.holidayDate",
    "holiday_date": "holidayDate",
}

print("Database Schema Migration Guide")
print("=" * 50)
print("\nOld Schema -> New MTPL Schema")
print("-" * 50)
for old, new in OLD_TO_NEW_MAPPING.items():
    print(f"{old:45} -> {new}")
