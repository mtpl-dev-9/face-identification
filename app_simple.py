import os
from datetime import datetime, timedelta
from typing import List
from dotenv import load_dotenv
from urllib.parse import quote_plus

from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from flask_cors import CORS
from flasgger import Swagger

# Load environment variables
load_dotenv()

from config import Config, calculate_distance, IST
from database import db
from models import Person, Attendance, Settings, AllowedIP, Holiday, User, LeaveAllotment, LeaveType, MonthlyReport
from multilevel_models import LeaveApprover, LeaveApproval
from multilevel_approval_apis import add_multilevel_approval_routes
from user_approvers_model import UserApprover
from user_approvers_api import add_user_approvers_routes
from sqlalchemy import and_, func
from datetime import date, datetime as dt
import pytz


def get_office_settings():
    """Get office settings from database or use defaults from config"""
    return {
        'latitude': float(Settings.get('office_latitude', Config.OFFICE_LATITUDE)),
        'longitude': float(Settings.get('office_longitude', Config.OFFICE_LONGITUDE)),
        'radius': float(Settings.get('geofence_radius', Config.GEOFENCE_RADIUS_METERS))
    }


def get_allowed_ips():
    """Get allowed IPs from database or use defaults from config"""
    ips = AllowedIP.get_all_active()
    return ips if ips else Config.ALLOWED_IPS


def get_ist_now():
    """Get current time in IST"""
    return dt.now(IST)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Load database configuration from .env
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.environ.get('DB_USER')}:{quote_plus(os.environ.get('DB_PASSWORD'))}@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'isolation_level': 'READ COMMITTED',
    }
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

    # folders
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), "instance"), exist_ok=True)

    db.init_app(app)
    CORS(app)
    
    # Initialize Swagger
    from swagger_config import swagger_config, swagger_template
    Swagger(app, config=swagger_config, template=swagger_template)

    with app.app_context():
        db.create_all()
    
    # Add multi-level approval routes
    add_multilevel_approval_routes(app, db)
    
    @app.route("/")
    def index():
        persons_count = Person.query.count()
        today_start = get_ist_now().replace(hour=0, minute=0, second=0, microsecond=0)
        attendance_today = Attendance.query.filter(
            Attendance.attendanceTimestamp >= today_start
        ).count()
        
        # Calculate absent count
        attended_person_ids = db.session.query(Attendance.attendanceUserId).filter(
            Attendance.attendanceTimestamp >= today_start,
            Attendance.attendanceClockInTime.isnot(None)
        ).distinct().all()
        attended_ids = [pid[0] for pid in attended_person_ids]
        absent_count = persons_count - len(attended_ids)
        
        return render_template(
            "index.html",
            persons_count=persons_count,
            attendance_today=attendance_today,
            absent_count=absent_count
        )

    @app.route("/api/users", methods=["GET"])
    def api_get_users():
        """Get All Users"""
        try:
            users = User.query.filter_by(userIsActive='1').all()
            return jsonify({
                "success": True,
                "users": [{
                    "user_id": u.userId,
                    "userId": u.userId,
                    "name": f"{u.userFirstName or ''} {u.userLastName or ''}".strip(),
                    "userFirstName": u.userFirstName or "",
                    "userLastName": u.userLastName or "",
                    "employee_code": u.userLogin or str(u.userId),
                    "userLogin": u.userLogin or ""
                } for u in users]
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)