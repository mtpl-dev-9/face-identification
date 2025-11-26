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
    biometricUserId = db.Column('biometricUserId', db.Integer, db.ForeignKey('mtpl_users.userId'), nullable=False)
    biometricEncoding = db.Column('biometricEncoding', db.Text, nullable=False)
    biometricCreatedAt = db.Column('biometricCreatedAt', db.DateTime, default=get_ist_now)
    biometricIsActive = db.Column('biometricIsActive', db.Boolean, default=True)

    # Relationship to user table
    user = db.relationship('User', backref='biometric_records')

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
        user_name = "Unknown"
        if self.user:
            user_name = f"{self.user.userFirstName} {self.user.userLastName}"
        
        return {
            "id": self.biometricId,
            "user_id": self.biometricUserId,
            "name": user_name,
            "employee_code": str(self.biometricUserId),
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


class Attendance(db.Model):
    __tablename__ = "mtpl_attendance"

    attendanceId = db.Column('attendanceId', db.Integer, primary_key=True)
    attendanceUserId = db.Column('attendanceUserId', db.Integer, db.ForeignKey("mtpl_users.userId"), nullable=False)
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

    user = db.relationship("User", backref="attendance_records")

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
        return self.user

    def to_dict(self):
        return {
            "id": self.attendanceId,
            "person_id": self.attendanceUserId,
            "person_name": f"{self.user.userFirstName} {self.user.userLastName}" if self.user else str(self.attendanceUserId),
            "employee_code": self.user.userLogin if self.user else str(self.attendanceUserId),
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
