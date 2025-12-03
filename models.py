from datetime import datetime, date, timedelta
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


class ManualTimeEntry(db.Model):
    __tablename__ = "mtpl_manual_time_entries"

    entryId = db.Column('entryId', db.Integer, primary_key=True)
    entryUserId = db.Column('entryUserId', db.Integer, nullable=False, index=True)
    entryWorkingDate = db.Column('entryWorkingDate', db.Date, nullable=False, index=True)
    entryCheckInTime = db.Column('entryCheckInTime', db.Time, nullable=True)
    entryCheckOutTime = db.Column('entryCheckOutTime', db.Time, nullable=True)
    entryBreakInTime = db.Column('entryBreakInTime', db.Time, nullable=True)
    entryBreakOutTime = db.Column('entryBreakOutTime', db.Time, nullable=True)
    entryCreatedAt = db.Column('entryCreatedAt', db.DateTime, default=get_ist_now)
    entryUpdatedAt = db.Column('entryUpdatedAt', db.DateTime, default=get_ist_now, onupdate=get_ist_now)
    entryCreatedBy = db.Column('entryCreatedBy', db.Integer, nullable=True)  # Admin user ID who created this entry

    @property
    def id(self):
        return self.entryId
    
    @property
    def user_id(self):
        return self.entryUserId
    
    @property
    def working_date(self):
        return self.entryWorkingDate
    
    @property
    def check_in_time(self):
        return self.entryCheckInTime
    
    @property
    def check_out_time(self):
        return self.entryCheckOutTime
    
    @property
    def break_in_time(self):
        return self.entryBreakInTime
    
    @property
    def break_out_time(self):
        return self.entryBreakOutTime

    def calculate_work_hours(self):
        """Calculate total work hours excluding break time"""
        if not self.entryCheckInTime or not self.entryCheckOutTime:
            return None
        
        # Convert times to datetime for calculation
        check_in = datetime.combine(self.entryWorkingDate, self.entryCheckInTime)
        check_out = datetime.combine(self.entryWorkingDate, self.entryCheckOutTime)
        
        # Handle case where check-out is next day
        if check_out < check_in:
            check_out += timedelta(days=1)
        
        total_time = check_out - check_in
        
        # Subtract break time if both break-in and break-out are present
        if self.entryBreakInTime and self.entryBreakOutTime:
            break_in = datetime.combine(self.entryWorkingDate, self.entryBreakInTime)
            break_out = datetime.combine(self.entryWorkingDate, self.entryBreakOutTime)
            
            # Handle case where break-out is next day
            if break_out < break_in:
                break_out += timedelta(days=1)
            
            break_duration = break_out - break_in
            total_time -= break_duration
        
        return total_time.total_seconds() / 3600  # Return hours as float

    def to_dict(self):
        user = User.query.filter_by(userId=self.entryUserId).first()
        user_name = f"{user.userFirstName} {user.userLastName}" if user else str(self.entryUserId)
        employee_code = user.userLogin if user else str(self.entryUserId)
        
        work_hours = self.calculate_work_hours()
        
        return {
            "id": self.entryId,
            "user_id": self.entryUserId,
            "user_name": user_name,
            "employee_code": employee_code,
            "working_date": self.entryWorkingDate.isoformat(),
            "check_in_time": self.entryCheckInTime.strftime('%H:%M:%S') if self.entryCheckInTime else None,
            "check_out_time": self.entryCheckOutTime.strftime('%H:%M:%S') if self.entryCheckOutTime else None,
            "break_in_time": self.entryBreakInTime.strftime('%H:%M:%S') if self.entryBreakInTime else None,
            "break_out_time": self.entryBreakOutTime.strftime('%H:%M:%S') if self.entryBreakOutTime else None,
            "work_hours": round(work_hours, 2) if work_hours is not None else None,
            "created_at": self.entryCreatedAt.isoformat() + "Z" if self.entryCreatedAt else None,
            "updated_at": self.entryUpdatedAt.isoformat() + "Z" if self.entryUpdatedAt else None,
            "created_by": self.entryCreatedBy
        }