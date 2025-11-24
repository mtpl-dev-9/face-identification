from datetime import datetime, date
from database import db
from sqlalchemy import and_
import pytz

IST = pytz.timezone('Asia/Kolkata')

def get_ist_now():
    return datetime.now(IST)


class Settings(db.Model):
    __tablename__ = "settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(200), nullable=False)
    updated_at = db.Column(db.DateTime, default=get_ist_now, onupdate=get_ist_now)

    @staticmethod
    def get(key, default=None):
        setting = Settings.query.filter_by(key=key).first()
        return setting.value if setting else default

    @staticmethod
    def set(key, value):
        setting = Settings.query.filter_by(key=key).first()
        if setting:
            setting.value = str(value)
            setting.updated_at = get_ist_now()
        else:
            setting = Settings(key=key, value=str(value))
            db.session.add(setting)
        db.session.commit()
        return setting


class AllowedIP(db.Model):
    __tablename__ = "allowed_ips"

    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=get_ist_now)

    def to_dict(self):
        return {
            "id": self.id,
            "ip_address": self.ip_address,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() + "Z"
        }

    @staticmethod
    def get_all_active():
        return [ip.ip_address for ip in AllowedIP.query.filter_by(is_active=True).all()]


class Person(db.Model):
    __tablename__ = "persons"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    employee_code = db.Column(db.String(50), unique=True, nullable=False)
    encoding = db.Column(db.Text, nullable=False)  # JSON of 128-d vector
    created_at = db.Column(db.DateTime, default=get_ist_now)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "employee_code": self.employee_code,
            "created_at": self.created_at.isoformat() + "Z",
            "is_active": self.is_active,
        }


class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey("persons.id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=get_ist_now, index=True)
    source = db.Column(db.String(50), default="live_camera")
    status = db.Column(db.String(20), default="present")
    action = db.Column(db.String(20), default="clock_in")  # clock_in or clock_out
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    clock_in_time = db.Column(db.DateTime, nullable=True)
    clock_out_time = db.Column(db.DateTime, nullable=True)

    person = db.relationship("Person", backref="attendance_records")

    def to_dict(self):
        return {
            "id": self.id,
            "person_id": self.person_id,
            "person_name": self.person.name if self.person else None,
            "employee_code": self.person.employee_code if self.person else None,
            "timestamp": self.timestamp.isoformat() + "Z",
            "source": self.source,
            "status": self.status,
            "action": self.action,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "ip_address": self.ip_address,
            "clock_in_time": self.clock_in_time.isoformat() + "Z" if self.clock_in_time else None,
            "clock_out_time": self.clock_out_time.isoformat() + "Z" if self.clock_out_time else None,
        }
