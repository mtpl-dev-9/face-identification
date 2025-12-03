from datetime import datetime, date
from database import db
from sqlalchemy import and_
import pytz

IST = pytz.timezone('Asia/Kolkata')

def get_ist_now():
    return datetime.now(IST)


class Settings(db.Model):
    __tablename__ = "mtpl_attendance_settings"

    settingId = db.Column('settingId', db.Integer, primary_key=True)
    settingKey = db.Column('settingKey', db.String(50), unique=True, nullable=False)
    settingValue = db.Column('settingValue', db.String(200), nullable=False)
    settingUpdatedAt = db.Column('settingUpdatedAt', db.DateTime, default=get_ist_now, onupdate=get_ist_now)

    @staticmethod
    def get(key, default=None):
        setting = Settings.query.filter_by(settingKey=key).first()
        return setting.settingValue if setting else default

    @staticmethod
    def set(key, value):
        setting = Settings.query.filter_by(settingKey=key).first()
        if setting:
            setting.settingValue = str(value)
            setting.settingUpdatedAt = get_ist_now()
        else:
            setting = Settings(settingKey=key, settingValue=str(value))
            db.session.add(setting)
        db.session.commit()
        return setting


class AllowedIP(db.Model):
    __tablename__ = "mtpl_allowed_ips"

    allowedIpId = db.Column('allowedIpId', db.Integer, primary_key=True)
    allowedIpAddress = db.Column('allowedIpAddress', db.String(50), unique=True, nullable=False)
    allowedIpDescription = db.Column('allowedIpDescription', db.String(200))
    allowedIpIsActive = db.Column('allowedIpIsActive', db.Boolean, default=True)
    allowedIpCreatedAt = db.Column('allowedIpCreatedAt', db.DateTime, default=get_ist_now)

    def to_dict(self):
        return {
            "id": self.allowedIpId,
            "ip_address": self.allowedIpAddress,
            "description": self.allowedIpDescription,
            "is_active": self.allowedIpIsActive,
            "created_at": self.allowedIpCreatedAt.isoformat() + "Z"
        }

    @staticmethod
    def get_all_active():
        return [ip.allowedIpAddress for ip in AllowedIP.query.filter_by(allowedIpIsActive=True).all()]


class Person(db.Model):
    __tablename__ = "mtpl_biometric"

    biometricId = db.Column('biometricId', db.Integer, primary_key=True)
    biometricUserId = db.Column('biometricUserId', db.Integer, nullable=False)
    biometricEncoding = db.Column('biometricEncoding', db.Text, nullable=False)
    biometricCreatedAt = db.Column('biometricCreatedAt', db.DateTime, default=get_ist_now)
    biometricIsActive = db.Column('biometricIsActive', db.Boolean, default=True)

    @property
    def id(self):
        return self.biometricId
    
    @property
    def encoding(self):
        return self.biometricEncoding
    
    @property
    def is_active(self):
        return self.biometricIsActive
    
    @property
    def created_at(self):
        return self.biometricCreatedAt

    def to_dict(self):
        user = User.query.filter_by(userId=self.biometricUserId).first()
        if user and user.userFirstName and user.userLastName:
            user_name = f"{user.userFirstName} {user.userLastName}".strip()
            employee_code = user.userLogin if user.userLogin else str(self.biometricUserId)
        else:
            user_name = f"User {self.biometricUserId}"
            employee_code = str(self.biometricUserId)
        
        return {
            "id": self.biometricId,
            "user_id": self.biometricUserId,
            "name": user_name,
            "employee_code": employee_code,
            "created_at": self.biometricCreatedAt.isoformat() + "Z" if self.biometricCreatedAt else None,
            "is_active": self.biometricIsActive,
        }


class User(db.Model):
    __tablename__ = "mtpl_users"

    userId = db.Column('userId', db.Integer, primary_key=True)
    userFirstName = db.Column('userFirstName', db.String(64))
    userLastName = db.Column('userLastName', db.String(64))
    userLogin = db.Column('userLogin', db.String(16))
    userIsActive = db.Column('userIsActive', db.String(1), default='1')

    @property
    def name(self):
        return f"{self.userFirstName} {self.userLastName}"
    
    @property
    def employee_code(self):
        return self.userLogin


class Holiday(db.Model):
    __tablename__ = "mtpl_holidays"

    holidayId = db.Column('holidayId', db.Integer, primary_key=True)
    holidayDate = db.Column('holidayDate', db.Date, unique=True, nullable=False, index=True)
    holidayName = db.Column('holidayName', db.String(100), nullable=False)
    holidayIsWeekoff = db.Column('holidayIsWeekoff', db.Boolean, default=False)
    holidayCreatedAt = db.Column('holidayCreatedAt', db.DateTime, default=get_ist_now)

    @property
    def id(self):
        return self.holidayId
    
    @property
    def date(self):
        return self.holidayDate
    
    @property
    def name(self):
        return self.holidayName
    
    @property
    def is_weekoff(self):
        return self.holidayIsWeekoff

    def to_dict(self):
        return {
            "id": self.holidayId,
            "date": self.holidayDate.isoformat(),
            "name": self.holidayName,
            "is_weekoff": self.holidayIsWeekoff,
            "created_at": self.holidayCreatedAt.isoformat() + "Z"
        }


class LeaveType(db.Model):
    __tablename__ = "mtpl_leave_types"

    leaveTypeId = db.Column('leaveTypeId', db.Integer, primary_key=True)
    leaveTypeName = db.Column('leaveTypeName', db.String(50), unique=True, nullable=False)
    leaveTypeIsPaid = db.Column('leaveTypeIsPaid', db.Boolean, default=True)
    leaveTypeIsEncashable = db.Column('leaveTypeIsEncashable', db.Boolean, default=False)
    leaveTypeRequireApproval = db.Column('leaveTypeRequireApproval', db.Boolean, default=True)
    leaveTypeRequireAttachment = db.Column('leaveTypeRequireAttachment', db.Boolean, default=False)
    leaveTypeIsActive = db.Column('leaveTypeIsActive', db.Boolean, default=True)
    leaveTypeCreatedAt = db.Column('leaveTypeCreatedAt', db.DateTime, default=get_ist_now)

    def to_dict(self):
        return {
            "id": self.leaveTypeId,
            "name": self.leaveTypeName,
            "is_paid": self.leaveTypeIsPaid,
            "is_encashable": self.leaveTypeIsEncashable,
            "require_approval": self.leaveTypeRequireApproval,
            "require_attachment": self.leaveTypeRequireAttachment,
            "is_active": self.leaveTypeIsActive,
            "created_at": self.leaveTypeCreatedAt.isoformat() + "Z"
        }


class UserLeaveBalance(db.Model):
    __tablename__ = "mtpl_user_leave_balance"

    balanceId = db.Column('balanceId', db.Integer, primary_key=True)
    balanceUserId = db.Column('balanceUserId', db.Integer, nullable=False, index=True)
    balanceLeaveTypeId = db.Column('balanceLeaveTypeId', db.Integer, db.ForeignKey('mtpl_leave_types.leaveTypeId'), nullable=False)
    balanceTotal = db.Column('balanceTotal', db.Integer, default=0)
    balanceUsed = db.Column('balanceUsed', db.Integer, default=0)
    balanceYear = db.Column('balanceYear', db.Integer, nullable=False, index=True)
    balanceUpdatedAt = db.Column('balanceUpdatedAt', db.DateTime, default=get_ist_now, onupdate=get_ist_now)

    leave_type = db.relationship('LeaveType', backref='balances')

    @property
    def remaining(self):
        return self.balanceTotal - self.balanceUsed

    def to_dict(self):
        return {
            "id": self.balanceId,
            "user_id": self.balanceUserId,
            "leave_type_id": self.balanceLeaveTypeId,
            "leave_type_name": self.leave_type.leaveTypeName,
            "total": self.balanceTotal,
            "used": self.balanceUsed,
            "remaining": self.remaining,
            "year": self.balanceYear
        }


class LeaveAllotment(db.Model):
    __tablename__ = "mtpl_leave_allotment"

    allotmentId = db.Column('allotmentId', db.Integer, primary_key=True)
    allotmentUserId = db.Column('allotmentUserId', db.Integer, nullable=False, index=True)
    allotmentLeaveTypeId = db.Column('allotmentLeaveTypeId', db.Integer, db.ForeignKey('mtpl_leave_types.leaveTypeId'), nullable=False)
    allotmentTotal = db.Column('allotmentTotal', db.Numeric(5, 1), nullable=False, default=0)
    allotmentYear = db.Column('allotmentYear', db.Integer, nullable=False, index=True)
    allotmentAssignedBy = db.Column('allotmentAssignedBy', db.Integer, nullable=True)
    allotmentAssignedAt = db.Column('allotmentAssignedAt', db.DateTime, default=get_ist_now)
    allotmentUpdatedAt = db.Column('allotmentUpdatedAt', db.DateTime, default=get_ist_now, onupdate=get_ist_now)

    leave_type = db.relationship('LeaveType', backref='allotments')

    def to_dict(self):
        user = User.query.filter_by(userId=self.allotmentUserId).first()
        user_name = f"{user.userFirstName} {user.userLastName}" if user else str(self.allotmentUserId)
        
        assigned_by_user = User.query.filter_by(userId=self.allotmentAssignedBy).first() if self.allotmentAssignedBy else None
        assigned_by_name = f"{assigned_by_user.userFirstName} {assigned_by_user.userLastName}" if assigned_by_user else None
        
        return {
            "id": self.allotmentId,
            "user_id": self.allotmentUserId,
            "user_name": user_name,
            "leave_type_id": self.allotmentLeaveTypeId,
            "leave_type_name": self.leave_type.leaveTypeName,
            "total": float(self.allotmentTotal),
            "year": self.allotmentYear,
            "assigned_by": self.allotmentAssignedBy,
            "assigned_by_name": assigned_by_name,
            "assigned_at": self.allotmentAssignedAt.isoformat() + "Z" if self.allotmentAssignedAt else None,
            "updated_at": self.allotmentUpdatedAt.isoformat() + "Z" if self.allotmentUpdatedAt else None
        }


class LeaveRequest(db.Model):
    __tablename__ = "mtpl_leave_requests"

    leaveRequestId = db.Column('leaveRequestId', db.Integer, primary_key=True)
    leaveRequestUserId = db.Column('leaveRequestUserId', db.Integer, nullable=False, index=True)
    leaveRequestLeaveTypeId = db.Column('leaveRequestLeaveTypeId', db.Integer, db.ForeignKey('mtpl_leave_types.leaveTypeId'), nullable=False)
    leaveRequestFromDate = db.Column('leaveRequestFromDate', db.Date, nullable=False)
    leaveRequestToDate = db.Column('leaveRequestToDate', db.Date, nullable=False)
    leaveRequestDays = db.Column('leaveRequestDays', db.Integer, nullable=False)
    leaveRequestReason = db.Column('leaveRequestReason', db.Text)
    leaveRequestStatus = db.Column('leaveRequestStatus', db.String(20), default='pending')  # pending, approved, rejected
    leaveRequestApprovedBy = db.Column('leaveRequestApprovedBy', db.Integer, nullable=True)
    leaveRequestApprovedAt = db.Column('leaveRequestApprovedAt', db.DateTime, nullable=True)
    leaveRequestCreatedAt = db.Column('leaveRequestCreatedAt', db.DateTime, default=get_ist_now)

    leave_type = db.relationship('LeaveType', backref='requests')

    def to_dict(self):
        user = User.query.filter_by(userId=self.leaveRequestUserId).first()
        user_name = f"{user.userFirstName} {user.userLastName}" if user else str(self.leaveRequestUserId)
        
        return {
            "id": self.leaveRequestId,
            "user_id": self.leaveRequestUserId,
            "user_name": user_name,
            "leave_type_id": self.leaveRequestLeaveTypeId,
            "leave_type_name": self.leave_type.leaveTypeName,
            "from_date": self.leaveRequestFromDate.isoformat(),
            "to_date": self.leaveRequestToDate.isoformat(),
            "days": self.leaveRequestDays,
            "reason": self.leaveRequestReason,
            "status": self.leaveRequestStatus,
            "approved_by": self.leaveRequestApprovedBy,
            "approved_at": self.leaveRequestApprovedAt.isoformat() + "Z" if self.leaveRequestApprovedAt else None,
            "created_at": self.leaveRequestCreatedAt.isoformat() + "Z"
        }


class MonthlyReport(db.Model):
    __tablename__ = "mtpl_monthly_reports"

    reportId = db.Column('reportId', db.Integer, primary_key=True)
    reportUserId = db.Column('reportUserId', db.Integer, nullable=False, index=True)
    reportMonth = db.Column('reportMonth', db.Integer, nullable=False)
    reportYear = db.Column('reportYear', db.Integer, nullable=False)
    reportTotalWorkingHours = db.Column('reportTotalWorkingHours', db.Numeric(10, 2), default=0)
    reportWorkedDays = db.Column('reportWorkedDays', db.Integer, default=0)
    reportTotalWeeklyOff = db.Column('reportTotalWeeklyOff', db.Integer, default=0)
    reportHolidays = db.Column('reportHolidays', db.Integer, default=0)
    reportLeavesTaken = db.Column('reportLeavesTaken', db.Numeric(5, 1), default=0)
    reportLeaveDetails = db.Column('reportLeaveDetails', db.Text, nullable=True)
    reportOnTimeEntries = db.Column('reportOnTimeEntries', db.Integer, default=0)
    reportEarlyOut = db.Column('reportEarlyOut', db.Integer, default=0)
    reportLateIn = db.Column('reportLateIn', db.Integer, default=0)
    reportAbsentDays = db.Column('reportAbsentDays', db.Integer, default=0)
    reportGeneratedAt = db.Column('reportGeneratedAt', db.DateTime, default=get_ist_now)
    reportUpdatedAt = db.Column('reportUpdatedAt', db.DateTime, default=get_ist_now, onupdate=get_ist_now)

    def to_dict(self):
        import json
        user = User.query.filter_by(userId=self.reportUserId).first()
        user_name = f"{user.userFirstName} {user.userLastName}" if user else str(self.reportUserId)
        
        leave_details = []
        if self.reportLeaveDetails:
            try:
                leave_details = json.loads(self.reportLeaveDetails)
            except:
                leave_details = []
        
        return {
            "id": self.reportId,
            "user_id": self.reportUserId,
            "user_name": user_name,
            "month": self.reportMonth,
            "year": self.reportYear,
            "total_working_hours": float(self.reportTotalWorkingHours),
            "worked_days": self.reportWorkedDays,
            "total_weekly_off": self.reportTotalWeeklyOff,
            "holidays": self.reportHolidays,
            "leaves_taken": float(self.reportLeavesTaken),
            "leave_details": leave_details,
            "on_time_entries": self.reportOnTimeEntries,
            "early_out": self.reportEarlyOut,
            "late_in": self.reportLateIn,
            "absent_days": self.reportAbsentDays,
            "generated_at": self.reportGeneratedAt.isoformat() + "Z" if self.reportGeneratedAt else None,
            "updated_at": self.reportUpdatedAt.isoformat() + "Z" if self.reportUpdatedAt else None
        }


class Attendance(db.Model):
    __tablename__ = "mtpl_attendance"

    attendanceId = db.Column('attendanceId', db.Integer, primary_key=True)
    attendanceUserId = db.Column('attendanceUserId', db.Integer, nullable=False)
    attendanceTimestamp = db.Column('attendanceTimestamp', db.DateTime, default=get_ist_now, index=True)
    attendanceSource = db.Column('attendanceSource', db.String(50), default="live_camera")
    attendanceStatus = db.Column('attendanceStatus', db.String(20), default="present")
    attendanceAction = db.Column('attendanceAction', db.String(20), default="clock_in")
    attendanceLatitude = db.Column('attendanceLatitude', db.Float, nullable=True)
    attendanceLongitude = db.Column('attendanceLongitude', db.Float, nullable=True)
    attendanceIpAddress = db.Column('attendanceIpAddress', db.String(50), nullable=True)
    attendanceClockInTime = db.Column('attendanceClockInTime', db.DateTime, nullable=True)
    attendanceClockOutTime = db.Column('attendanceClockOutTime', db.DateTime, nullable=True)
    attendanceBreakInTime = db.Column('attendanceBreakInTime', db.DateTime, nullable=True)
    attendanceBreakOutTime = db.Column('attendanceBreakOutTime', db.DateTime, nullable=True)

    @property
    def id(self):
        return self.attendanceId
    
    @property
    def person_id(self):
        return self.attendanceUserId
    
    @property
    def timestamp(self):
        return self.attendanceTimestamp
    
    @property
    def clock_in_time(self):
        return self.attendanceClockInTime
    
    @property
    def clock_out_time(self):
        return self.attendanceClockOutTime
    
    @property
    def break_in_time(self):
        return self.attendanceBreakInTime
    
    @property
    def break_out_time(self):
        return self.attendanceBreakOutTime
    
    @property
    def action(self):
        return self.attendanceAction
    
    @property
    def person(self):
        return Person.query.filter_by(biometricUserId=self.attendanceUserId).first()
    
    def to_dict(self):
        user = User.query.filter_by(userId=self.attendanceUserId).first()
        person_name = f"{user.userFirstName} {user.userLastName}" if user else str(self.attendanceUserId)
        employee_code = user.userLogin if user else str(self.attendanceUserId)
        
        return {
            "id": self.attendanceId,
            "person_id": self.attendanceUserId,
            "person_name": person_name,
            "employee_code": employee_code,
            "timestamp": self.attendanceTimestamp.isoformat() + "Z",
            "source": self.attendanceSource,
            "status": self.attendanceStatus,
            "action": self.attendanceAction,
            "latitude": self.attendanceLatitude,
            "longitude": self.attendanceLongitude,
            "ip_address": self.attendanceIpAddress,
            "clock_in_time": self.attendanceClockInTime.isoformat() + "Z" if self.attendanceClockInTime else None,
            "clock_out_time": self.attendanceClockOutTime.isoformat() + "Z" if self.attendanceClockOutTime else None,
            "break_in_time": self.attendanceBreakInTime.isoformat() + "Z" if self.attendanceBreakInTime else None,
            "break_out_time": self.attendanceBreakOutTime.isoformat() + "Z" if self.attendanceBreakOutTime else None,
        }
