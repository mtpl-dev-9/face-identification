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
from models import Person, Attendance, Settings, AllowedIP, Holiday, User, LeaveAllotment, LeaveType, MonthlyReport, ManualTimeEntry
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
from face_utils import (
    load_image_from_file_storage,
    load_image_from_base64,
    get_face_encodings,
    encode_to_json,
    decode_from_json,
    check_face_exists,
    FACE_RECOGNITION_AVAILABLE,
)

try:
    import face_recognition  # type: ignore
except Exception as e:  # pragma: no cover - environment-dependent
    face_recognition = None  # type: ignore
    import logging

    logging.warning("Face recognition modules not available in app.py: %s", e)
    print("Warning: Face recognition modules not available:", e)
    print("Manual time entry and other non-face-recognition features will still work.")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Load database configuration from environment (with sensible defaults)
    db_user = os.environ.get("DB_USER") or "root"
    db_password = os.environ.get("DB_PASSWORD") or "zeenalbca"
    db_host = os.environ.get("DB_HOST") or "localhost"
    db_port = os.environ.get("DB_PORT") or "3306"
    db_name = os.environ.get("DB_NAME") or "mtpl_website"

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{db_user}:{quote_plus(db_password)}@{db_host}:{db_port}/{db_name}"
    )
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
    
    # Add user approvers routes (simple version)
    @app.route("/api/user-approvers-simple", methods=["GET"])
    def api_get_user_approvers_simple():
        """
        Get User Approvers
        ---
        tags:
          - Multi-Level Approval
        parameters:
          - name: user_id
            in: query
            type: integer
            description: Filter by user ID
        responses:
          200:
            description: List of user approver assignments
        """
        try:
            from user_approvers_model import UserApprover
            user_id = request.args.get('user_id', type=int)
            
            query = UserApprover.query.filter_by(userApproverIsActive=True)
            if user_id:
                query = query.filter_by(userApproverUserId=user_id)
            
            assignments = query.all()
            return jsonify({
                "success": True, 
                "assignments": [a.to_dict() for a in assignments]
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route("/api/user-approvers-simple", methods=["POST"])
    def api_assign_approvers_simple():
        """
        Assign Approvers to User
        ---
        tags:
          - Multi-Level Approval
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                user_id:
                  type: integer
                  description: User ID to assign approvers to
                approver_ids:
                  type: array
                  items:
                    type: integer
                  description: List of approver IDs
        responses:
          200:
            description: Approvers assigned successfully
        """
        try:
            from user_approvers_model import UserApprover
            data = request.get_json() or {}
            user_id = data.get('user_id')
            approver_ids = data.get('approver_ids', [])
            
            if not user_id or not approver_ids:
                return jsonify({"success": False, "error": "user_id and approver_ids required"}), 400
            
            # Clear existing
            UserApprover.query.filter_by(userApproverUserId=user_id).delete()
            
            # Add new
            assignments = []
            for approver_id in approver_ids:
                assignment = UserApprover(
                    userApproverUserId=user_id,
                    userApproverApproverId=approver_id
                )
                db.session.add(assignment)
                assignments.append(assignment)
            
            db.session.commit()
            
            return jsonify({
                "success": True,
                "count": len(assignments),
                "assignments": [a.to_dict() for a in assignments]
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 500

    # ---------- API: Get Users ----------
    @app.route("/api/users", methods=["GET"])
    def api_get_users():
        """
        Get All Users
        ---
        tags:
          - User Management
        responses:
          200:
            description: List of all active users
        """
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

    # ---------- API: Manual Time Entries ----------
    @app.route("/api/manual-time-entries", methods=["GET"])
    def api_get_manual_time_entries():
        """
        Get Manual Time Entries
        ---
        tags:
          - Manual Time Entry
        parameters:
          - name: user_id
            in: query
            type: integer
            required: false
          - name: from_date
            in: query
            type: string
            format: date
          - name: to_date
            in: query
            type: string
            format: date
        responses:
          200:
            description: List of manual time entries
        """
        try:
            query = ManualTimeEntry.query

            user_id = request.args.get("user_id", type=int)
            from_date_str = request.args.get("from_date")
            to_date_str = request.args.get("to_date")

            if user_id:
                query = query.filter_by(entryUserId=user_id)

            if from_date_str:
                from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
                query = query.filter(ManualTimeEntry.entryWorkingDate >= from_date)

            if to_date_str:
                to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
                query = query.filter(ManualTimeEntry.entryWorkingDate <= to_date)

            entries = query.order_by(
                ManualTimeEntry.entryWorkingDate.desc(),
                ManualTimeEntry.entryUserId.asc(),
            ).all()

            return jsonify(
                {
                    "success": True,
                    "entries": [e.to_dict() for e in entries],
                }
            )
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/manual-time-entries", methods=["POST"])
    def api_create_manual_time_entry():
        """
        Create / Update Manual Time Entry
        ---
        tags:
          - Manual Time Entry
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                user_id:
                  type: integer
                working_date:
                  type: string
                  format: date
                check_in_time:
                  type: string
                  format: time
                check_out_time:
                  type: string
                  format: time
                break_in_time:
                  type: string
                  format: time
                break_out_time:
                  type: string
                  format: time
        responses:
          200:
            description: Manual time entry saved
        """
        try:
            data = request.get_json() or {}

            user_id = data.get("user_id")
            working_date_str = data.get("working_date")
            check_in_time_str = data.get("check_in_time")
            check_out_time_str = data.get("check_out_time")
            break_in_time_str = data.get("break_in_time")
            break_out_time_str = data.get("break_out_time")
            created_by = data.get("created_by")

            if not user_id or not working_date_str:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "user_id and working_date are required",
                        }
                    ),
                    400,
                )

            try:
                working_date = datetime.strptime(working_date_str, "%Y-%m-%d").date()
            except ValueError:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Invalid working_date format. Use YYYY-MM-DD",
                        }
                    ),
                    400,
                )

            def parse_time(value):
                if not value:
                    return None
                try:
                    return datetime.strptime(value, "%H:%M").time()
                except ValueError:
                    try:
                        return datetime.strptime(value, "%H:%M:%S").time()
                    except ValueError:
                        return None

            check_in_time = parse_time(check_in_time_str)
            check_out_time = parse_time(check_out_time_str)
            break_in_time = parse_time(break_in_time_str)
            break_out_time = parse_time(break_out_time_str)

            if any(
                [
                    check_in_time_str and not check_in_time,
                    check_out_time_str and not check_out_time,
                    break_in_time_str and not break_in_time,
                    break_out_time_str and not break_out_time,
                ]
            ):
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Invalid time format. Use HH:MM or HH:MM:SS",
                        }
                    ),
                    400,
                )

            # Ensure user exists and is active
            user = User.query.filter_by(userId=user_id, userIsActive="1").first()
            if not user:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "User not found or inactive",
                        }
                    ),
                    404,
                )

            # Upsert by (user, date)
            entry = ManualTimeEntry.query.filter_by(
                entryUserId=user_id, entryWorkingDate=working_date
            ).first()

            if not entry:
                entry = ManualTimeEntry(
                    entryUserId=user_id,
                    entryWorkingDate=working_date,
                )
                db.session.add(entry)

            entry.entryCheckInTime = check_in_time
            entry.entryCheckOutTime = check_out_time
            entry.entryBreakInTime = break_in_time
            entry.entryBreakOutTime = break_out_time

            # Track who created / updated this manual entry (e.g. Admin = 1, Manager = 2, User = 7)
            if created_by is not None:
                try:
                    entry.entryCreatedBy = int(created_by)
                except (TypeError, ValueError):
                    entry.entryCreatedBy = entry.entryCreatedBy or 1
            else:
                # Default to Admin (1) when coming from this UI, so value is stored in DB but not shown
                entry.entryCreatedBy = entry.entryCreatedBy or 1

            db.session.commit()

            return jsonify({"success": True, "entry": entry.to_dict()})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 500

    # ---------- helper: match face ----------
    def match_single_encoding(encoding):
        if not FACE_RECOGNITION_AVAILABLE or face_recognition is None:
            # Face recognition backend not available – skip matching
            return None, None

        persons: List[Person] = Person.query.filter_by(biometricIsActive=True).all()
        if not persons:
            return None, None

        known_encodings = [decode_from_json(p.biometricEncoding) for p in persons]
        known_labels = persons

        distances = face_recognition.face_distance(known_encodings, encoding)
        best_idx = int(distances.argmin())
        best_distance = float(distances[best_idx])

        if best_distance <= app.config["FACE_RECOGNITION_TOLERANCE"]:
            return known_labels[best_idx], best_distance
        return None, best_distance

    # ---------- views ----------

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

    @app.route("/manual-time-entries")
    def manual_time_entries_view():
        """Simple admin UI to view and manage manual time entries."""
        users = User.query.filter_by(userIsActive='1').order_by(User.userFirstName.asc()).all()
        return render_template("manual_time_entries.html", users=users)

    @app.route("/api/analytics/dashboard")
    def api_analytics_dashboard():
        """
        Get Dashboard Analytics
        ---
        tags:
          - Analytics
        responses:
          200:
            description: Dashboard statistics
        """
        now = get_ist_now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Today's stats
        today_records = Attendance.query.filter(
            Attendance.attendanceTimestamp >= today_start,
            Attendance.attendanceClockInTime.isnot(None)
        ).all()
        
        late_count = sum(1 for r in today_records if r.attendanceClockInTime and r.attendanceClockInTime.hour >= 10)
        overtime_count = sum(1 for r in today_records if r.attendanceClockOutTime and r.attendanceClockOutTime.hour >= 18)
        
        # Calculate absent count
        attended_person_ids = db.session.query(Attendance.attendanceUserId).filter(
            Attendance.attendanceTimestamp >= today_start,
            Attendance.attendanceClockInTime.isnot(None)
        ).distinct().all()
        attended_ids = [pid[0] for pid in attended_person_ids]
        total_persons = Person.query.count()
        absent_count = total_persons - len(attended_ids)
        
        # Weekly data
        weekly_data = []
        for i in range(7):
            day = week_start + timedelta(days=i)
            day_end = day + timedelta(days=1)
            count = Attendance.query.filter(
                Attendance.attendanceTimestamp >= day,
                Attendance.attendanceTimestamp < day_end,
                Attendance.attendanceClockInTime.isnot(None)
            ).count()
            weekly_data.append({"day": day.strftime("%a"), "count": count})
        
        # Monthly data (last 30 days)
        monthly_data = []
        for i in range(30):
            day = today_start - timedelta(days=29-i)
            day_end = day + timedelta(days=1)
            count = Attendance.query.filter(
                Attendance.attendanceTimestamp >= day,
                Attendance.attendanceTimestamp < day_end,
                Attendance.attendanceClockInTime.isnot(None)
            ).count()
            monthly_data.append({"date": day.strftime("%d"), "count": count})
        
        return jsonify({
            "today": {
                "total": len(today_records),
                "late": late_count,
                "overtime": overtime_count,
                "ontime": len(today_records) - late_count,
                "absent": absent_count
            },
            "weekly": weekly_data,
            "monthly": monthly_data
        })

    # --- register with upload ---
    @app.route("/register", methods=["GET", "POST"])
    def register_view():
        if request.method == "GET":
            return render_template("register.html")

        name = request.form.get("name")
        user_id = request.form.get("employee_code")  # Using as user ID
        image_file = request.files.get("image")

        if not name or not user_id or not image_file:
            flash("Name, user ID and image are required", "danger")
            return redirect(request.url)

        try:
            user_id_int = int(user_id)
        except ValueError:
            flash("User ID must be a number", "danger")
            return redirect(request.url)

        # Check if user exists and is active
        user = User.query.filter_by(userId=user_id_int, userIsActive='1').first()
        if not user:
            flash("User ID not found or inactive", "danger")
            return redirect(request.url)

        # Check if user ID already has biometric
        if Person.query.filter_by(biometricUserId=user_id_int).first():
            flash("Face already registered for this user ID", "danger")
            return redirect(request.url)

        img_array = load_image_from_file_storage(image_file)
        encodings = get_face_encodings(img_array)

        if not encodings:
            flash("No face found in the image. Try another photo.", "warning")
            return redirect(request.url)
        if len(encodings) > 1:
            flash("Multiple faces detected. Please upload a photo with only one face.", "warning")
            return redirect(request.url)

        # Check if face already registered
        all_persons = Person.query.filter_by(biometricIsActive=True).all()
        existing_encodings = [decode_from_json(p.biometricEncoding) for p in all_persons]
        
        if check_face_exists(encodings[0], existing_encodings, tolerance=app.config["FACE_RECOGNITION_TOLERANCE"]):
            flash("This face is already registered. Cannot register the same person twice.", "danger")
            return redirect(request.url)

        encoding_json = encode_to_json(encodings[0])
        person = Person(biometricUserId=user_id_int, biometricEncoding=encoding_json)
        db.session.add(person)
        db.session.commit()

        flash(f"Registered user ID {user_id} successfully", "success")
        return redirect(url_for("index"))
    @app.route("/api/register-face-live", methods=["POST"])
    def api_register_face_live():
       try:
           data = request.get_json() or {}
           user_id = data.get("user_id") or data.get("employee_code")
           image_data = data.get("image")

           if not user_id or not image_data:
               return jsonify({"success": False, "error": "User ID and image required"}), 400

           try:
               user_id_int = int(user_id)
           except ValueError:
               return jsonify({"success": False, "error": "Invalid user ID"}), 400

           # Check if user exists and is active
           user = User.query.filter_by(userId=user_id_int, userIsActive='1').first()
           if not user:
               return jsonify({"success": False, "error": "User not found or inactive"}), 404

           # Check if user is currently clocked in
           now = get_ist_now()
           today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
           today_record = Attendance.query.filter(
               and_(
                   Attendance.attendanceUserId == user_id_int,
                   Attendance.attendanceTimestamp >= today_start,
                   Attendance.attendanceClockInTime.isnot(None)
               )
           ).order_by(Attendance.attendanceTimestamp.desc()).first()
           
           if today_record and today_record.attendanceClockOutTime is None:
               return jsonify({"success": False, "error": "Please clock out first before re-registering your face"}), 403

           # Check if user already has biometric 
           existing_person = Person.query.filter_by(biometricUserId=user_id_int, biometricIsActive=True).first()
           if existing_person:
               # Deactivate old biometric instead of deleting
               existing_person.biometricIsActive = False
               db.session.commit()

           img_array = load_image_from_base64(image_data)
           encodings = get_face_encodings(img_array)

           if not encodings:
               return jsonify({"success": False, "error": "No face detected"}), 422
           if len(encodings) > 1:
               return jsonify({"success": False, "error": "Multiple faces detected. Please show only one face."}), 422

           # Check if face already registered - EXCLUDE current user
           all_persons = Person.query.filter(
               Person.biometricIsActive == True,
               Person.biometricUserId != user_id_int
           ).all()
           existing_encodings = [decode_from_json(p.biometricEncoding) for p in all_persons]
           
           if existing_encodings and check_face_exists(encodings[0], existing_encodings, tolerance=app.config["FACE_RECOGNITION_TOLERANCE"]):
               return jsonify({"success": False, "error": "This face is already registered to another user"}), 400

           encoding_json = encode_to_json(encodings[0])
           person = Person(biometricUserId=user_id_int, biometricEncoding=encoding_json)
           db.session.add(person)
           db.session.commit()

           return jsonify({"success": True, "person": person.to_dict()})
       except Exception as e:
           db.session.rollback()
           return jsonify({"success": False, "error": str(e)}), 500

    # --- people list ---
    @app.route("/persons")
    def persons_view():
        persons = Person.query.order_by(Person.biometricCreatedAt.desc()).all()
        return render_template("persons.html", persons=persons)

    @app.route("/api/persons", methods=["GET"])
    def api_get_persons():
        persons = Person.query.filter_by(biometricIsActive=True).order_by(Person.biometricCreatedAt.desc()).all()
        return jsonify({"success": True, "persons": [p.to_dict() for p in persons]})

    @app.route("/api/users/bulk", methods=["POST"])
    def api_bulk_add_users():
        try:
            data = request.get_json() or {}
            employees = data.get('employees', [])
            
            if not employees:
                return jsonify({"success": False, "error": "No employees provided"}), 400
            
            added = []
            for emp in employees:
                firstName = emp.get('firstName', '').strip()
                lastName = emp.get('lastName', '').strip()
                login = emp.get('login', '').strip()
                
                if not firstName or not login:
                    continue
                
                if User.query.filter_by(userLogin=login).first():
                    continue
                
                user = User(userFirstName=firstName, userLastName=lastName, userLogin=login, userIsActive='1')
                db.session.add(user)
                added.append(user)
            
            db.session.commit()
            return jsonify({"success": True, "count": len(added)})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/persons/<int:person_id>", methods=["DELETE", "POST"])
    def api_delete_person(person_id):
        try:
            person = Person.query.get(person_id)
            if not person:
                return jsonify({"success": False, "error": "Person not found"}), 404
            
            # Delete associated attendance records first
            Attendance.query.filter_by(attendanceUserId=person.biometricUserId).delete()
            
            # Delete person
            db.session.delete(person)
            db.session.commit()
            
            return jsonify({"success": True, "message": "Person deleted successfully"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 500

    # --- attendance log view ---
    @app.route("/attendance")
    def attendance_view():
        records = Attendance.query.order_by(Attendance.attendanceTimestamp.desc()).limit(100).all()
        return render_template("attendance.html", records=records)

    @app.route("/attendance/report")
    def attendance_report_view():
        records = Attendance.query.order_by(Attendance.attendanceTimestamp.desc()).limit(100).all()
        return render_template("attendance_report.html", records=records)

    # --- live attendance camera page ---
    @app.route("/attendance/live")
    def attendance_live_view():
        return render_template("live_attendance.html")

    # --- clock in/out page ---
    @app.route("/attendance/clock")
    def attendance_clock_view():
        return render_template("clock_attendance.html")

    # --- get office location helper ---
    @app.route("/get-location")
    def get_location_view():
        return render_template("get_location.html")

    # --- settings page ---
    @app.route("/settings")
    def settings_view():
        office_settings = get_office_settings()
        return render_template("settings.html", settings=office_settings)

    @app.route("/api/settings", methods=["GET"])
    def api_get_settings():
        """
        Get Office Settings
        ---
        tags:
          - Settings
        responses:
          200:
            description: Office settings
        """
        return jsonify(get_office_settings())

    @app.route("/api/settings", methods=["POST"])
    def api_update_settings():
        """
        Update Office Settings
        ---
        tags:
          - Settings
        parameters:
          - name: body
            in: body
            schema:
              type: object
              properties:
                latitude:
                  type: number
                longitude:
                  type: number
                radius:
                  type: number
        responses:
          200:
            description: Settings updated
        """
        data = request.get_json() or {}
        
        if 'latitude' in data:
            Settings.set('office_latitude', data['latitude'])
        if 'longitude' in data:
            Settings.set('office_longitude', data['longitude'])
        if 'radius' in data:
            Settings.set('geofence_radius', data['radius'])
        
        return jsonify({"success": True, "settings": get_office_settings()})

    @app.route("/api/allowed-ips", methods=["GET"])
    def api_get_allowed_ips():
        ips = AllowedIP.query.all()
        return jsonify({"success": True, "ips": [ip.to_dict() for ip in ips]})

    @app.route("/api/allowed-ips", methods=["POST"])
    def api_add_allowed_ip():
        data = request.get_json() or {}
        ip_address = data.get('ip_address')
        description = data.get('description', '')
        
        if not ip_address:
            return jsonify({"success": False, "error": "IP address required"}), 400
        
        if AllowedIP.query.filter_by(ip_address=ip_address).first():
            return jsonify({"success": False, "error": "IP already exists"}), 400
        
        ip = AllowedIP(ip_address=ip_address, description=description)
        db.session.add(ip)
        db.session.commit()
        
        return jsonify({"success": True, "ip": ip.to_dict()})

    @app.route("/api/allowed-ips/<int:ip_id>", methods=["DELETE"])
    def api_delete_allowed_ip(ip_id):
        ip = AllowedIP.query.get(ip_id)
        if not ip:
            return jsonify({"success": False, "error": "IP not found"}), 404
        
        db.session.delete(ip)
        db.session.commit()
        
        return jsonify({"success": True})

    @app.route("/api/allowed-ips/<int:ip_id>/toggle", methods=["POST"])
    def api_toggle_allowed_ip(ip_id):
        ip = AllowedIP.query.get(ip_id)
        if not ip:
            return jsonify({"success": False, "error": "IP not found"}), 404
        
        ip.is_active = not ip.is_active
        db.session.commit()
        
        return jsonify({"success": True, "ip": ip.to_dict()})

    # ---------- APIs ----------

    @app.route("/api/biometric/check/<int:user_id>", methods=["GET"])
    def api_check_biometric(user_id):
        """Check if user has biometric registered"""
        person = Person.query.filter_by(biometricUserId=user_id, biometricIsActive=True).first()
        return jsonify({
            "success": True,
            "hasBiometric": person is not None,
            "biometricId": person.biometricId if person else None
        })

    @app.route("/api/attendance/check-status/<int:user_id>", methods=["GET"])
    def api_check_attendance_status(user_id):
        """Check if user is currently clocked in"""
        now = get_ist_now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        today_record = Attendance.query.filter(
            and_(
                Attendance.attendanceUserId == user_id,
                Attendance.attendanceTimestamp >= today_start,
                Attendance.attendanceClockInTime.isnot(None)
            )
        ).order_by(Attendance.attendanceTimestamp.desc()).first()
        
        is_clocked_in = today_record is not None and today_record.attendanceClockOutTime is None
        
        return jsonify({
            "success": True,
            "isClockedIn": is_clocked_in
        })

    @app.route("/api/biometric/<int:user_id>", methods=["DELETE"])
    def api_delete_biometric(user_id):
        """Deactivate user's biometric data"""
        try:
            person = Person.query.filter_by(biometricUserId=user_id).first()
            if not person:
                return jsonify({"success": False, "error": "No biometric found"}), 404
            person.biometricIsActive = False
            db.session.commit()
            return jsonify({"success": True, "message": "Biometric deactivated successfully"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/register-face", methods=["POST"])
    def api_register_face():
        name = request.form.get("name")
        user_id = request.form.get("employee_code")
        image_file = request.files.get("image")

        if not name or not user_id or not image_file:
            return jsonify({"success": False, "error": "name, user_id, image required"}), 400

        try:
            user_id_int = int(user_id)
        except ValueError:
            return jsonify({"success": False, "error": "user_id must be number"}), 400

        # Check if user exists and is active
        user = User.query.filter_by(userId=user_id_int, userIsActive='1').first()
        if not user:
            return jsonify({"success": False, "error": "user not found or inactive"}), 404

        # Check if user ID already has biometric
        if Person.query.filter_by(biometricUserId=user_id_int).first():
            return jsonify({"success": False, "error": "face already registered"}), 400

        img_array = load_image_from_file_storage(image_file)
        encodings = get_face_encodings(img_array)

        if not encodings:
            return jsonify({"success": False, "error": "no face found"}), 422
        if len(encodings) > 1:
            return jsonify({"success": False, "error": "multiple faces found"}), 422

        # Check if face already registered
        all_persons = Person.query.filter_by(biometricIsActive=True).all()
        existing_encodings = [decode_from_json(p.biometricEncoding) for p in all_persons]
        
        if check_face_exists(encodings[0], existing_encodings, tolerance=app.config["FACE_RECOGNITION_TOLERANCE"]):
            return jsonify({"success": False, "error": "face already registered"}), 400

        encoding_json = encode_to_json(encodings[0])
        person = Person(biometricUserId=user_id_int, biometricEncoding=encoding_json)
        db.session.add(person)
        db.session.commit()

        return jsonify({"success": True, "person": person.to_dict()})

    @app.route("/api/attendance/clock", methods=["POST"])
    def api_attendance_clock():
        """
        Clock In/Out with Face Recognition
        ---
        tags:
          - Attendance
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                image:
                  type: string
                action:
                  type: string
                  enum: [clock_in, clock_out]
                latitude:
                  type: number
                longitude:
                  type: number
        responses:
          200:
            description: Success
        """
        data = request.get_json(silent=True) or {}
        user_id = data.get("user_id")
        image_data = data.get("image")
        action = data.get("action")
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if not image_data or not action:
            return jsonify({"success": False, "error": "image and action required"}), 400

        if action not in ["clock_in", "clock_out"]:
            return jsonify({"success": False, "error": "action must be clock_in or clock_out"}), 400

        # Check face first
        img_array = load_image_from_base64(image_data)
        encodings = get_face_encodings(img_array)

        if not encodings:
            return jsonify({"success": False, "error": "No face detected"}), 422

        encoding = encodings[0]
        person, face_distance = match_single_encoding(encoding)

        if not person:
            return jsonify({"success": False, "error": "Unknown face"}), 404

        # If user_id provided, verify face matches
        if user_id and person.biometricUserId != int(user_id):
            return jsonify({"success": False, "error": "Face does not match authenticated user. Please use your own registered face."}), 403

        # Then check IP and location
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ',' in client_ip:
            client_ip = client_ip.split(',')[0].strip()

        allowed_ips = get_allowed_ips()
        if client_ip not in allowed_ips:
            return jsonify({"success": False, "error": f"Access denied. IP {client_ip} not allowed"}), 403

        if latitude is None or longitude is None:
            return jsonify({"success": False, "error": "Location required"}), 400

        office_settings = get_office_settings()
        distance_from_office = calculate_distance(
            office_settings['latitude'],
            office_settings['longitude'],
            float(latitude),
            float(longitude)
        )

        if distance_from_office > office_settings['radius']:
            return jsonify({
                "success": False,
                "error": f"You are {distance_from_office:.2f}m away. Must be within {office_settings['radius']}m"
            }), 403

        # Verify user is still active
        user = User.query.filter_by(userId=person.biometricUserId, userIsActive='1').first()
        if not user:
            return jsonify({"success": False, "error": "User account is inactive"}), 403

        now = get_ist_now()
        today = now.date()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        today_record = Attendance.query.filter(
            and_(
                Attendance.attendanceUserId == person.biometricUserId,
                Attendance.attendanceTimestamp >= today_start
            )
        ).order_by(Attendance.attendanceTimestamp.desc()).first()

        if action == "clock_in":
            if today_record and today_record.attendanceAction == "clock_in" and not today_record.attendanceClockOutTime:
                return jsonify({"success": False, "error": "Already clocked in. Clock out first"}), 400

            record = Attendance(
                attendanceUserId=person.biometricUserId,
                attendanceStatus="present",
                attendanceSource="live_camera",
                attendanceAction="clock_in",
                attendanceLatitude=latitude,
                attendanceLongitude=longitude,
                attendanceIpAddress=client_ip,
                attendanceClockInTime=now,
                attendanceTimestamp=now
            )
            db.session.add(record)
            db.session.commit()
            message = f"Clocked in at {now.strftime('%H:%M:%S')}"

        else:
            if not today_record or today_record.attendanceAction != "clock_in":
                return jsonify({"success": False, "error": "No clock-in found. Clock in first"}), 400

            if today_record.attendanceClockOutTime:
                return jsonify({"success": False, "error": "Already clocked out today"}), 400

            today_record.attendanceClockOutTime = now
            today_record.attendanceAction = "clock_out"
            db.session.commit()
            record = today_record
            message = f"Clocked out at {now.strftime('%H:%M:%S')}"

        return jsonify({
            "success": True,
            "person": person.to_dict(),
            "attendance": record.to_dict(),
            "message": message,
            "distance_from_office": round(distance_from_office, 2)
        })

    @app.route("/api/attendance/live-mark", methods=["POST"])
    def api_attendance_live_mark():
        data = request.get_json(silent=True) or {}
        image_data = data.get("image")

        if not image_data:
            return jsonify({"success": False, "error": "image field (dataURL) required"}), 400

        img_array = load_image_from_base64(image_data)
        encodings = get_face_encodings(img_array)

        if not encodings:
            return jsonify({"success": True, "match": False, "message": "No face detected"})

        # Only consider the first face for attendance
        encoding = encodings[0]
        person, distance = match_single_encoding(encoding)

        if not person:
            return jsonify({"success": True, "match": False, "message": "Unknown face"})

        now = get_ist_now()

        # prevent spam: only one record per person per minute
        last = Attendance.query.filter_by(attendanceUserId=person.biometricUserId).order_by(Attendance.attendanceTimestamp.desc()).first()
        if not last or (now - last.attendanceTimestamp) > timedelta(minutes=1):
            record = Attendance(attendanceUserId=person.biometricUserId, attendanceStatus="present", attendanceSource="live_camera")
            db.session.add(record)
            db.session.commit()
        else:
            record = last

        return jsonify(
            {
                "success": True,
                "match": True,
                "person": person.to_dict(),
                "distance": float(distance),
                "attendance": record.to_dict(),
            }
        )

    @app.route("/api/attendance/latest", methods=["GET"])
    def api_attendance_latest():
        """
        Get Latest Attendance Records
        ---
        tags:
          - Attendance
        responses:
          200:
            description: Latest 20 records
        """
        records = Attendance.query.order_by(Attendance.attendanceTimestamp.desc()).limit(20).all()
        return jsonify(
            {
                "success": True,
                "results": [r.to_dict() for r in records],
            }
        )

    @app.route("/api/attendance/today/<user_id>", methods=["GET"])
    def api_attendance_today(user_id):
        """
        Get Today's Attendance
        ---
        tags:
          - Attendance
        parameters:
          - name: user_id
            in: path
            required: true
            type: string
        responses:
          200:
            description: Today's attendance record
        """
        now = get_ist_now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        record = Attendance.query.filter(
            Attendance.attendanceUserId == user_id,
            Attendance.attendanceTimestamp >= today_start,
            Attendance.attendanceClockInTime.isnot(None)
        ).order_by(Attendance.attendanceTimestamp.desc()).first()
        if not record:
            return jsonify({"success": True, "attendance": None}), 404
        return jsonify({"success": True, "attendance": record.to_dict()})

    @app.route("/api/attendance/break", methods=["POST"])
    def api_attendance_break():
        """
        Break In/Out
        ---
        tags:
          - Attendance
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                action:
                  type: string
                  enum: [break_in, break_out]
                latitude:
                  type: number
                longitude:
                  type: number
        responses:
          200:
            description: Break recorded
        """
        data = request.get_json(silent=True) or {}
        action = data.get("action")
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if not action:
            return jsonify({"success": False, "error": "action required"}), 400

        if action not in ["break_in", "break_out"]:
            return jsonify({"success": False, "error": "action must be break_in or break_out"}), 400

        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ',' in client_ip:
            client_ip = client_ip.split(',')[0].strip()

        allowed_ips = get_allowed_ips()
        if client_ip not in allowed_ips:
            return jsonify({"success": False, "error": f"Access denied. IP {client_ip} not allowed"}), 403

        if latitude is None or longitude is None:
            return jsonify({"success": False, "error": "Location required"}), 400

        office_settings = get_office_settings()
        distance_from_office = calculate_distance(
            office_settings['latitude'],
            office_settings['longitude'],
            float(latitude),
            float(longitude)
        )

        if distance_from_office > office_settings['radius']:
            return jsonify({
                "success": False,
                "error": f"You are {distance_from_office:.2f}m away. Must be within {office_settings['radius']}m"
            }), 403

        now = get_ist_now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Find today's attendance record with clock_in
        today_record = Attendance.query.filter(
            Attendance.attendanceTimestamp >= today_start,
            Attendance.attendanceClockInTime.isnot(None)
        ).order_by(Attendance.attendanceTimestamp.desc()).first()

        if not today_record:
            return jsonify({"success": False, "error": "No clock-in found today. Please clock in first"}), 400

        if action == "break_in":
            if today_record.attendanceBreakInTime and not today_record.attendanceBreakOutTime:
                return jsonify({"success": False, "error": "Already on break. Break out first"}), 400
            
            today_record.attendanceBreakInTime = now
            message = f"Break started at {now.strftime('%H:%M:%S')}"
        else:
            if not today_record.attendanceBreakInTime:
                return jsonify({"success": False, "error": "No break-in found. Break in first"}), 400
            
            if today_record.attendanceBreakOutTime:
                return jsonify({"success": False, "error": "Already broke out"}), 400
            
            today_record.attendanceBreakOutTime = now
            message = f"Break ended at {now.strftime('%H:%M:%S')}"

        db.session.commit()

        return jsonify({
            "success": True,
            "attendance": today_record.to_dict(),
            "message": message,
            "distance_from_office": round(distance_from_office, 2)
        })

    # --- holidays/leave management ---
    @app.route("/holidays")
    def holidays_view():
        return render_template("holidays.html")

    @app.route("/api/holidays", methods=["GET"])
    def api_get_holidays():
        """
        Get Holidays for Month
        ---
        tags:
          - Holidays
        parameters:
          - name: year
            in: query
            type: integer
          - name: month
            in: query
            type: integer
        responses:
          200:
            description: List of holidays
        """
        year = request.args.get('year', get_ist_now().year, type=int)
        month = request.args.get('month', get_ist_now().month, type=int)
        
        holidays = Holiday.query.filter(
            func.extract('year', Holiday.holidayDate) == year,
            func.extract('month', Holiday.holidayDate) == month
        ).all()
        
        return jsonify({"success": True, "holidays": [h.to_dict() for h in holidays]})

    @app.route("/api/holidays", methods=["POST"])
    def api_add_holiday():
        """
        Add New Holiday
        ---
        tags:
          - Holidays
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                date:
                  type: string
                name:
                  type: string
                is_weekoff:
                  type: boolean
        responses:
          200:
            description: Holiday added
        """
        try:
            data = request.get_json() or {}
            date_str = data.get('date')
            name = data.get('name')
            is_weekoff = data.get('is_weekoff', False)
            
            if not date_str or not name:
                return jsonify({"success": False, "error": "Date and name required"}), 400
            
            try:
                holiday_date = dt.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"success": False, "error": "Invalid date format. Use YYYY-MM-DD"}), 400
            
            if Holiday.query.filter_by(holidayDate=holiday_date).first():
                return jsonify({"success": False, "error": "Holiday already exists for this date"}), 400
            
            holiday = Holiday(holidayDate=holiday_date, holidayName=name, holidayIsWeekoff=is_weekoff)
            db.session.add(holiday)
            db.session.commit()
            
            return jsonify({"success": True, "holiday": holiday.to_dict()})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": f"Database error: {str(e)}"}), 500

    @app.route("/api/holidays/<int:holiday_id>", methods=["DELETE"])
    def api_delete_holiday(holiday_id):
        holiday = Holiday.query.get(holiday_id)
        if not holiday:
            return jsonify({"success": False, "error": "Holiday not found"}), 404
        
        db.session.delete(holiday)
        db.session.commit()
        
        return jsonify({"success": True})

    # --- Leave Management ---
    @app.route("/leave-management")
    def leave_management():
        return render_template("leave_management.html")

    @app.route("/api/leave-creation-form", methods=["GET"])
    def api_get_leave_types():
        """
        Get All Leave Types
        ---
        tags:
          - Leave Management
        responses:
          200:
            description: List of active leave types
        """
        from models import LeaveType
        leave_types = LeaveType.query.filter_by(leaveTypeIsActive=True).all()
        return jsonify({"success": True, "leave_types": [lt.to_dict() for lt in leave_types]})

    @app.route("/api/leave-creation-form", methods=["POST"])
    def api_add_leave_type():
        try:
            from models import LeaveType
            data = request.get_json() or {}
            name = data.get('name', '').strip()
            is_paid = bool(data.get('is_paid', True))
            is_encashable = bool(data.get('is_encashable', False))
            require_approval = bool(data.get('require_approval', True))
            require_attachment = bool(data.get('require_attachment', False))
            
            if not name:
                return jsonify({"success": False, "error": "Leave type name required"}), 400
            
            existing = LeaveType.query.filter_by(leaveTypeName=name).first()
            if existing:
                if existing.leaveTypeIsActive:
                    return jsonify({"success": False, "error": "Leave creation form already exists"}), 400
                existing.leaveTypeIsActive = True
                existing.leaveTypeIsPaid = is_paid
                existing.leaveTypeIsEncashable = is_encashable
                existing.leaveTypeRequireApproval = require_approval
                existing.leaveTypeRequireAttachment = require_attachment
                db.session.commit()
                return jsonify({"success": True, "leave_type": existing.to_dict()})
            
            leave_type = LeaveType(
                leaveTypeName=name,
                leaveTypeIsPaid=is_paid,
                leaveTypeIsEncashable=is_encashable,
                leaveTypeRequireApproval=require_approval,
                leaveTypeRequireAttachment=require_attachment
            )
            db.session.add(leave_type)
            db.session.commit()
            db.session.refresh(leave_type)
            
            print(f"DEBUG: Saved leave type ID={leave_type.leaveTypeId}, Name={leave_type.leaveTypeName}")
            
            return jsonify({"success": True, "leave_type": leave_type.to_dict()})
        except Exception as e:
            db.session.rollback()
            print(f"ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/leave-creation-form/<int:leave_type_id>", methods=["PUT"])
    def api_update_leave_type(leave_type_id):
        """
        Update Leave Type
        ---
        tags:
          - Leave Management
        parameters:
          - name: leave_type_id
            in: path
            type: integer
            required: true
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                name:
                  type: string
                is_paid:
                  type: boolean
                is_encashable:
                  type: boolean
                require_approval:
                  type: boolean
                require_attachment:
                  type: boolean
        responses:
          200:
            description: Leave type updated
        """
        from models import LeaveType
        leave_type = LeaveType.query.get(leave_type_id)
        if not leave_type:
            return jsonify({"success": False, "error": "Leave type not found"}), 404
        
        data = request.get_json() or {}
        if 'name' in data:
            leave_type.leaveTypeName = data['name'].strip()
        if 'is_paid' in data:
            leave_type.leaveTypeIsPaid = bool(data['is_paid'])
        if 'is_encashable' in data:
            leave_type.leaveTypeIsEncashable = bool(data['is_encashable'])
        if 'require_approval' in data:
            leave_type.leaveTypeRequireApproval = bool(data['require_approval'])
        if 'require_attachment' in data:
            leave_type.leaveTypeRequireAttachment = bool(data['require_attachment'])
        
        db.session.commit()
        return jsonify({"success": True, "leave_type": leave_type.to_dict()})

    @app.route("/api/leave-creation-form/<int:leave_type_id>", methods=["DELETE"])
    def api_delete_leave_type(leave_type_id):
        """
        Delete Leave Type
        ---
        tags:
          - Leave Management
        parameters:
          - name: leave_type_id
            in: path
            type: integer
            required: true
        responses:
          200:
            description: Leave type deleted
        """
        from models import LeaveType
        leave_type = LeaveType.query.get(leave_type_id)
        if not leave_type:
            return jsonify({"success": False, "error": "Leave type not found"}), 404
        
        leave_type.leaveTypeIsActive = False
        db.session.commit()
        
        return jsonify({"success": True})

    @app.route("/api/user-leave-balance", methods=["GET"])
    def api_get_user_leave_balance():
        """
        Get User Leave Balance
        ---
        tags:
          - Leave Management
        parameters:
          - name: user_id
            in: query
            type: integer
            required: true
          - name: year
            in: query
            type: integer
        responses:
          200:
            description: User leave balances
        """
        from models import UserLeaveBalance
        user_id = request.args.get('user_id', type=int)
        year = request.args.get('year', get_ist_now().year, type=int)
        
        if not user_id:
            return jsonify({"success": False, "error": "user_id required"}), 400
        
        balances = UserLeaveBalance.query.filter_by(balanceUserId=user_id, balanceYear=year).all()
        return jsonify({"success": True, "balances": [b.to_dict() for b in balances]})

    @app.route("/api/user-leave-balance/rollover", methods=["POST"])
    def api_rollover_leave_balance():
        """
        Rollover Leave Balance to New Year
        ---
        tags:
          - Leave Management
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                from_year:
                  type: integer
                to_year:
                  type: integer
                user_ids:
                  type: array
                  items:
                    type: integer
        responses:
          200:
            description: Leave balances rolled over
        """
        from models import UserLeaveBalance
        data = request.get_json() or {}
        from_year = data.get('from_year')
        to_year = data.get('to_year')
        user_ids = data.get('user_ids', [])
        
        if not from_year or not to_year:
            return jsonify({"success": False, "error": "from_year and to_year required"}), 400
        
        if not user_ids:
            return jsonify({"success": False, "error": "user_ids required"}), 400
        
        created = []
        for user_id in user_ids:
            old_balances = UserLeaveBalance.query.filter_by(
                balanceUserId=user_id,
                balanceYear=from_year
            ).all()
            
            for old_bal in old_balances:
                existing = UserLeaveBalance.query.filter_by(
                    balanceUserId=user_id,
                    balanceLeaveTypeId=old_bal.balanceLeaveTypeId,
                    balanceYear=to_year
                ).first()
                
                if not existing:
                    new_bal = UserLeaveBalance(
                        balanceUserId=user_id,
                        balanceLeaveTypeId=old_bal.balanceLeaveTypeId,
                        balanceTotal=old_bal.balanceTotal,
                        balanceUsed=0,
                        balanceYear=to_year
                    )
                    db.session.add(new_bal)
                    created.append(new_bal)
        
        db.session.commit()
        return jsonify({"success": True, "count": len(created)})

    @app.route("/api/user-leave-balance/default", methods=["POST"])
    def api_set_default_leave_balance():
        """
        Assign Default Leave Balance to All Users
        ---
        tags:
          - Leave Management
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                year:
                  type: integer
                defaults:
                  type: object
                  properties:
                    casual:
                      type: number
                    sick:
                      type: number
                    celebratory:
                      type: number
        responses:
          200:
            description: Default leaves assigned
        """
        from models import UserLeaveBalance, LeaveType
        data = request.get_json() or {}
        year = data.get('year', get_ist_now().year)
        defaults = data.get('defaults', {'casual': 4, 'sick': 7, 'celebratory': 0.5})
        
        users = User.query.filter_by(userIsActive='1').all()
        if not users:
            return jsonify({"success": False, "error": "No users found"}), 404
        
        leave_types = {}
        for name in ['Casual Leave', 'Sick Leave', 'Celebratory Leave']:
            lt = LeaveType.query.filter_by(leaveTypeName=name).first()
            if not lt:
                lt = LeaveType(leaveTypeName=name)
                db.session.add(lt)
                db.session.flush()
            leave_types[name] = lt
        
        mapping = {
            'Casual Leave': defaults.get('casual', 4),
            'Sick Leave': defaults.get('sick', 7),
            'Celebratory Leave': defaults.get('celebratory', 0.5)
        }
        
        count = 0
        for user in users:
            for leave_name, total in mapping.items():
                leave_type = leave_types[leave_name]
                balance = UserLeaveBalance.query.filter_by(
                    balanceUserId=user.userId,
                    balanceLeaveTypeId=leave_type.leaveTypeId,
                    balanceYear=year
                ).first()
                
                if balance:
                    balance.balanceTotal = total
                else:
                    balance = UserLeaveBalance(
                        balanceUserId=user.userId,
                        balanceLeaveTypeId=leave_type.leaveTypeId,
                        balanceTotal=total,
                        balanceYear=year
                    )
                    db.session.add(balance)
                count += 1
        
        db.session.commit()
        return jsonify({"success": True, "count": count, "users": len(users)})

    @app.route("/api/user-leave-balance/bulk", methods=["POST"])
    def api_set_bulk_user_leave_balance():
        """
        Assign Leave Balance to Multiple Users
        ---
        tags:
          - Leave Management
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                user_ids:
                  type: array
                  items:
                    type: integer
                leave_type_id:
                  type: integer
                total:
                  type: number
                year:
                  type: integer
        responses:
          200:
            description: Leave balance assigned to multiple users
        """
        from models import UserLeaveBalance
        data = request.get_json() or {}
        user_ids = data.get('user_ids', [])
        leave_type_id = data.get('leave_type_id')
        total = data.get('total', 0)
        year = data.get('year', get_ist_now().year)
        
        if not user_ids or not leave_type_id:
            return jsonify({"success": False, "error": "user_ids and leave_type_id required"}), 400
        
        results = []
        for user_id in user_ids:
            balance = UserLeaveBalance.query.filter_by(
                balanceUserId=user_id,
                balanceLeaveTypeId=leave_type_id,
                balanceYear=year
            ).first()
            
            if balance:
                balance.balanceTotal = total
            else:
                balance = UserLeaveBalance(
                    balanceUserId=user_id,
                    balanceLeaveTypeId=leave_type_id,
                    balanceTotal=total,
                    balanceYear=year
                )
                db.session.add(balance)
            results.append(balance)
        
        db.session.commit()
        return jsonify({"success": True, "count": len(results), "balances": [b.to_dict() for b in results]})

    @app.route("/api/user-leave-balance", methods=["POST"])
    def api_set_user_leave_balance():
        """
        Assign Leave Balance
        ---
        tags:
          - Leave Management
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                user_id:
                  type: integer
                leave_type_id:
                  type: integer
                total:
                  type: number
                year:
                  type: integer
        responses:
          200:
            description: Leave balance assigned
        """
        from models import UserLeaveBalance
        data = request.get_json() or {}
        user_id = data.get('user_id')
        leave_type_id = data.get('leave_type_id')
        total = data.get('total', 0)
        year = data.get('year', get_ist_now().year)
        
        if not user_id or not leave_type_id:
            return jsonify({"success": False, "error": "user_id and leave_type_id required"}), 400
        
        balance = UserLeaveBalance.query.filter_by(
            balanceUserId=user_id,
            balanceLeaveTypeId=leave_type_id,
            balanceYear=year
        ).first()
        
        if balance:
            balance.balanceTotal = total
        else:
            balance = UserLeaveBalance(
                balanceUserId=user_id,
                balanceLeaveTypeId=leave_type_id,
                balanceTotal=total,
                balanceYear=year
            )
            db.session.add(balance)
        
        db.session.commit()
        return jsonify({"success": True, "balance": balance.to_dict()})

    @app.route("/api/leave-requests", methods=["GET"])
    def api_get_leave_requests():
        """
        Get Leave Requests
        ---
        tags:
          - Leave Management
        parameters:
          - name: user_id
            in: query
            type: integer
          - name: status
            in: query
            type: string
            enum: [pending, approved, rejected]
        responses:
          200:
            description: List of leave requests
        """
        from models import LeaveRequest
        user_id = request.args.get('user_id', type=int)
        status = request.args.get('status')
        
        query = LeaveRequest.query
        if user_id:
            query = query.filter_by(leaveRequestUserId=user_id)
        if status:
            query = query.filter_by(leaveRequestStatus=status)
        
        requests = query.order_by(LeaveRequest.leaveRequestCreatedAt.desc()).all()
        return jsonify({"success": True, "requests": [r.to_dict() for r in requests]})

    @app.route("/api/leave-requests", methods=["POST"])
    def api_create_leave_request():
        """
        Create Leave Request
        ---
        tags:
          - Leave Management
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                user_id:
                  type: integer
                leave_type_id:
                  type: integer
                from_date:
                  type: string
                  format: date
                to_date:
                  type: string
                  format: date
                day_type:
                  type: string
                  enum: [full, half]
                reason:
                  type: string
        responses:
          200:
            description: Leave request created
        """
        from models import LeaveRequest, UserLeaveBalance
        data = request.get_json() or {}
        user_id = data.get('user_id')
        leave_type_id = data.get('leave_type_id')
        from_date_str = data.get('from_date')
        to_date_str = data.get('to_date')
        day_type = data.get('day_type', 'full')
        reason = data.get('reason', '')
        
        if not all([user_id, leave_type_id, from_date_str, to_date_str]):
            return jsonify({"success": False, "error": "All fields required"}), 400
        
        try:
            from_date = dt.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = dt.strptime(to_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"success": False, "error": "Invalid date format"}), 400
        
        if to_date < from_date:
            return jsonify({"success": False, "error": "To date must be after from date"}), 400
        
        # Calculate days based on day_type
        base_days = (to_date - from_date).days + 1
        if day_type == 'half' and base_days == 1:
            days = 0.5
        else:
            days = float(base_days)
        year = from_date.year
        
        allotment = LeaveAllotment.query.filter_by(
            allotmentUserId=user_id,
            allotmentLeaveTypeId=leave_type_id,
            allotmentYear=year
        ).first()
        
        if not allotment:
            return jsonify({"success": False, "error": "No leave allotment found"}), 400
        
        used_leaves = db.session.query(func.sum(LeaveRequest.leaveRequestDays)).filter(
            LeaveRequest.leaveRequestUserId == user_id,
            LeaveRequest.leaveRequestLeaveTypeId == leave_type_id,
            LeaveRequest.leaveRequestStatus == 'approved',
            func.extract('year', LeaveRequest.leaveRequestFromDate) == year
        ).scalar() or 0
        
        remaining = float(allotment.allotmentTotal) - float(used_leaves)
        if remaining < days:
            return jsonify({"success": False, "error": f"Insufficient leave balance. Available: {remaining}, Requested: {days}"}), 400
        
        leave_request = LeaveRequest(
            leaveRequestUserId=user_id,
            leaveRequestLeaveTypeId=leave_type_id,
            leaveRequestFromDate=from_date,
            leaveRequestToDate=to_date,
            leaveRequestDays=days,
            leaveRequestReason=reason
        )
        db.session.add(leave_request)
        db.session.commit()
        
        return jsonify({"success": True, "request": leave_request.to_dict()})

    @app.route("/api/leave-requests/<int:request_id>/approve", methods=["POST"])
    def api_approve_leave_request(request_id):
        """
        Approve Leave Request
        ---
        tags:
          - Leave Management
        parameters:
          - name: request_id
            in: path
            type: integer
            required: true
          - name: body
            in: body
            schema:
              type: object
              properties:
                approved_by:
                  type: integer
        responses:
          200:
            description: Leave request approved
        """
        from models import LeaveRequest, UserLeaveBalance
        data = request.get_json() or {}
        approved_by = data.get('approved_by')
        
        leave_request = LeaveRequest.query.get(request_id)
        if not leave_request:
            return jsonify({"success": False, "error": "Request not found"}), 404
        
        if leave_request.leaveRequestStatus != 'pending':
            return jsonify({"success": False, "error": "Request already processed"}), 400
        
        leave_request.leaveRequestStatus = 'approved'
        leave_request.leaveRequestApprovedBy = approved_by
        leave_request.leaveRequestApprovedAt = get_ist_now()
        
        db.session.commit()
        return jsonify({"success": True, "request": leave_request.to_dict()})

    @app.route("/api/leave-requests/<int:request_id>/reject", methods=["POST"])
    def api_reject_leave_request(request_id):
        """
        Reject Leave Request
        ---
        tags:
          - Leave Management
        parameters:
          - name: request_id
            in: path
            type: integer
            required: true
          - name: body
            in: body
            schema:
              type: object
              properties:
                approved_by:
                  type: integer
        responses:
          200:
            description: Leave request rejected
        """
        from models import LeaveRequest
        data = request.get_json() or {}
        approved_by = data.get('approved_by')
        
        leave_request = LeaveRequest.query.get(request_id)
        if not leave_request:
            return jsonify({"success": False, "error": "Request not found"}), 404
        
        if leave_request.leaveRequestStatus != 'pending':
            return jsonify({"success": False, "error": "Request already processed"}), 400
        
        leave_request.leaveRequestStatus = 'rejected'
        leave_request.leaveRequestApprovedBy = approved_by
        leave_request.leaveRequestApprovedAt = get_ist_now()
        
        db.session.commit()
        return jsonify({"success": True, "request": leave_request.to_dict()})

    #  --- Leave Allotment APIs ---
    @app.route("/api/leave-allotments", methods=["GET"])
    def api_get_leave_allotments():
        """
        Get Leave Allotments
        ---
        tags:
          - Leave Allotment
        parameters:
          - name: user_id
            in: query
            type: integer
          - name: year
            in: query
            type: integer
        responses:
          200:
            description: List of leave allotments with used/remaining
        """
        from models import LeaveRequest
        user_id = request.args.get('user_id', type=int)
        year = request.args.get('year', get_ist_now().year, type=int)
        
        query = LeaveAllotment.query
        if user_id:
            query = query.filter_by(allotmentUserId=user_id)
        if year:
            query = query.filter_by(allotmentYear=year)
        
        allotments = query.order_by(LeaveAllotment.allotmentAssignedAt.desc()).all()
        result = []
        for a in allotments:
            used = db.session.query(func.sum(LeaveRequest.leaveRequestDays)).filter(
                LeaveRequest.leaveRequestUserId == a.allotmentUserId,
                LeaveRequest.leaveRequestLeaveTypeId == a.allotmentLeaveTypeId,
                LeaveRequest.leaveRequestStatus == 'approved',
                func.extract('year', LeaveRequest.leaveRequestFromDate) == a.allotmentYear
            ).scalar() or 0
            data = a.to_dict()
            data['used'] = float(used)
            data['remaining'] = float(a.allotmentTotal) - float(used)
            result.append(data)
        return jsonify({"success": True, "allotments": result})

    @app.route("/api/leave-allotments", methods=["POST"])
    def api_create_leave_allotment():
        """
        Create Leave Allotment
        ---
        tags:
          - Leave Allotment
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                user_id:
                  type: integer
                leave_type_id:
                  type: integer
                total:
                  type: number
                year:
                  type: integer
                assigned_by:
                  type: integer
        responses:
          200:
            description: Leave allotment created
        """
        data = request.get_json() or {}
        user_id = data.get('user_id')
        leave_type_id = data.get('leave_type_id')
        total = data.get('total', 0)
        year = data.get('year', get_ist_now().year)
        assigned_by = data.get('assigned_by')
        
        if not user_id or not leave_type_id:
            return jsonify({"success": False, "error": "user_id and leave_type_id required"}), 400
        
        existing = LeaveAllotment.query.filter_by(
            allotmentUserId=user_id,
            allotmentLeaveTypeId=leave_type_id,
            allotmentYear=year
        ).first()
        
        if existing:
            existing.allotmentTotal = total
            existing.allotmentAssignedBy = assigned_by
            existing.allotmentUpdatedAt = get_ist_now()
            db.session.commit()
            return jsonify({"success": True, "allotment": existing.to_dict()})
        
        allotment = LeaveAllotment(
            allotmentUserId=user_id,
            allotmentLeaveTypeId=leave_type_id,
            allotmentTotal=total,
            allotmentYear=year,
            allotmentAssignedBy=assigned_by
        )
        db.session.add(allotment)
        db.session.commit()
        
        return jsonify({"success": True, "allotment": allotment.to_dict()})

    @app.route("/api/leave-allotments/bulk", methods=["POST"])
    def api_create_bulk_leave_allotment():
        """
        Bulk Create Leave Allotments
        ---
        tags:
          - Leave Allotment
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                user_ids:
                  type: array
                  items:
                    type: integer
                leave_type_id:
                  type: integer
                total:
                  type: number
                year:
                  type: integer
                assigned_by:
                  type: integer
        responses:
          200:
            description: Leave allotments created for multiple users
        """
        data = request.get_json() or {}
        user_ids = data.get('user_ids', [])
        leave_type_id = data.get('leave_type_id')
        total = data.get('total', 0)
        year = data.get('year', get_ist_now().year)
        assigned_by = data.get('assigned_by')
        
        if not user_ids or not leave_type_id:
            return jsonify({"success": False, "error": "user_ids and leave_type_id required"}), 400
        
        results = []
        for user_id in user_ids:
            existing = LeaveAllotment.query.filter_by(
                allotmentUserId=user_id,
                allotmentLeaveTypeId=leave_type_id,
                allotmentYear=year
            ).first()
            
            if existing:
                existing.allotmentTotal = total
                existing.allotmentAssignedBy = assigned_by
                existing.allotmentUpdatedAt = get_ist_now()
                results.append(existing)
            else:
                allotment = LeaveAllotment(
                    allotmentUserId=user_id,
                    allotmentLeaveTypeId=leave_type_id,
                    allotmentTotal=total,
                    allotmentYear=year,
                    allotmentAssignedBy=assigned_by
                )
                db.session.add(allotment)
                results.append(allotment)
        
        db.session.flush()
        db.session.commit()
        
        # Verify data was written
        verify_count = LeaveAllotment.query.filter_by(allotmentYear=year, allotmentLeaveTypeId=leave_type_id).count()
        
        return jsonify({"success": True, "count": len(results), "verified_in_db": verify_count, "allotments": [a.to_dict() for a in results]})

    @app.route("/api/leave-allotments/<int:allotment_id>", methods=["DELETE"])
    def api_delete_leave_allotment(allotment_id):
        """
        Delete Leave Allotment
        ---
        tags:
          - Leave Allotment
        parameters:
          - name: allotment_id
            in: path
            type: integer
            required: true
        responses:
          200:
            description: Leave allotment deleted
        """
        allotment = LeaveAllotment.query.get(allotment_id)
        if not allotment:
            return jsonify({"success": False, "error": "Allotment not found"}), 404
        
        db.session.delete(allotment)
        db.session.commit()
        
        return jsonify({"success": True})

    @app.route("/api/leave-allotments/default", methods=["POST"])
    def api_assign_default_leave_allotments():
        """
        Assign Default Leave Allotments to All Users
        ---
        tags:
          - Leave Allotment
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                year:
                  type: integer
                defaults:
                  type: object
                  properties:
                    casual:
                      type: number
                    sick:
                      type: number
                    celebratory:
                      type: number
                assigned_by:
                  type: integer
        responses:
          200:
            description: Default leaves assigned
        """
        from models import LeaveType
        data = request.get_json() or {}
        year = data.get('year', get_ist_now().year)
        defaults = data.get('defaults', {'casual': 4, 'sick': 7, 'celebratory': 0.5})
        assigned_by = data.get('assigned_by')
        
        users = User.query.filter_by(userIsActive='1').all()
        if not users:
            return jsonify({"success": False, "error": "No users found"}), 404
        
        leave_types = {}
        for name in ['Casual Leave', 'Sick Leave', 'Celebratory Leave']:
            lt = LeaveType.query.filter_by(leaveTypeName=name).first()
            if not lt:
                lt = LeaveType(leaveTypeName=name)
                db.session.add(lt)
                db.session.flush()
            leave_types[name] = lt
        
        mapping = {
            'Casual Leave': defaults.get('casual', 4),
            'Sick Leave': defaults.get('sick', 7),
            'Celebratory Leave': defaults.get('celebratory', 0.5)
        }
        
        count = 0
        for user in users:
            for leave_name, total in mapping.items():
                leave_type = leave_types[leave_name]
                allotment = LeaveAllotment.query.filter_by(
                    allotmentUserId=user.userId,
                    allotmentLeaveTypeId=leave_type.leaveTypeId,
                    allotmentYear=year
                ).first()
                
                if allotment:
                    allotment.allotmentTotal = total
                    allotment.allotmentAssignedBy = assigned_by
                    allotment.allotmentUpdatedAt = get_ist_now()
                else:
                    allotment = LeaveAllotment(
                        allotmentUserId=user.userId,
                        allotmentLeaveTypeId=leave_type.leaveTypeId,
                        allotmentTotal=total,
                        allotmentYear=year,
                        allotmentAssignedBy=assigned_by
                    )
                    db.session.add(allotment)
                count += 1
        
        db.session.commit()
        return jsonify({"success": True, "count": count, "users": len(users)})

    @app.route("/api/attendance/monthly-report", methods=["GET"])
    def api_monthly_attendance_report():
        """
        Generate Monthly Attendance Report
        ---
        tags:
          - Reports
        parameters:
          - name: user_id
            in: query
            type: integer
            required: true
            description: User ID
          - name: month
            in: query
            type: integer
            required: true
            description: Month (1-12)
          - name: year
            in: query
            type: integer
            required: true
            description: Year
        responses:
          200:
            description: Monthly report generated and saved
        """
        from models import LeaveRequest
        from calendar import monthrange
        
        user_id = request.args.get('user_id', type=int)
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        if not user_id or not month or not year:
            return jsonify({"success": False, "error": "user_id, month, year required"}), 400
        
        month_start = dt(year, month, 1, tzinfo=IST)
        days_in_month = monthrange(year, month)[1]
        month_end = dt(year, month, days_in_month, 23, 59, 59, tzinfo=IST)
        
        records = Attendance.query.filter(
            Attendance.attendanceUserId == user_id,
            Attendance.attendanceTimestamp >= month_start,
            Attendance.attendanceTimestamp <= month_end,
            Attendance.attendanceClockInTime.isnot(None)
        ).all()
        
        holidays = Holiday.query.filter(
            func.extract('year', Holiday.holidayDate) == year,
            func.extract('month', Holiday.holidayDate) == month
        ).all()
        holiday_dates = {h.holidayDate for h in holidays}
        weekoff_dates = {h.holidayDate for h in holidays if h.holidayIsWeekoff}
        
        leaves = LeaveRequest.query.filter(
            LeaveRequest.leaveRequestUserId == user_id,
            LeaveRequest.leaveRequestStatus == 'approved',
            LeaveRequest.leaveRequestFromDate <= month_end.date(),
            LeaveRequest.leaveRequestToDate >= month_start.date()
        ).all()
        leave_days = sum(l.leaveRequestDays for l in leaves)
        
        # Group leaves by type
        leave_summary = {}
        for l in leaves:
            lt = LeaveType.query.get(l.leaveRequestLeaveTypeId)
            if lt:
                if lt.leaveTypeName not in leave_summary:
                    leave_summary[lt.leaveTypeName] = {
                        'type': lt.leaveTypeName,
                        'days': 0,
                        'is_paid': bool(lt.leaveTypeIsPaid)
                    }
                leave_summary[lt.leaveTypeName]['days'] += float(l.leaveRequestDays)
        
        leave_details = list(leave_summary.values())
        
        total_hours = 0
        on_time = 0
        late_in = 0
        early_out = 0
        
        for r in records:
            if r.attendanceClockInTime and r.attendanceClockOutTime:
                break_duration = 0
                if r.attendanceBreakInTime and r.attendanceBreakOutTime:
                    break_duration = (r.attendanceBreakOutTime - r.attendanceBreakInTime).total_seconds() / 3600
                work_duration = (r.attendanceClockOutTime - r.attendanceClockInTime).total_seconds() / 3600 - break_duration
                total_hours += work_duration
            
            if r.attendanceClockInTime and r.attendanceClockInTime.hour < 10:
                on_time += 1
            elif r.attendanceClockInTime:
                late_in += 1
            
            if r.attendanceClockOutTime and r.attendanceClockOutTime.hour < 18:
                early_out += 1
        
        worked_days = len(records)
        total_weekoffs = len(weekoff_dates)
        total_holidays = len(holiday_dates) - total_weekoffs
        working_days = days_in_month - total_weekoffs - total_holidays
        absent_days = working_days - worked_days - leave_days
        
        report_data = {
            "user_id": user_id,
            "month": month,
            "year": year,
            "total_working_hours": round(total_hours, 2),
            "worked_days": worked_days,
            "total_weekly_off": total_weekoffs,
            "holidays": total_holidays,
            "leaves_taken": leave_days,
            "leave_details": leave_details,
            "on_time_entries": on_time,
            "early_out": early_out,
            "late_in": late_in,
            "absent_days": max(0, absent_days)
        }
        
        import json
        leave_details_json = json.dumps(leave_details)
        
        existing = MonthlyReport.query.filter_by(reportUserId=user_id, reportMonth=month, reportYear=year).first()
        if existing:
            existing.reportTotalWorkingHours = report_data['total_working_hours']
            existing.reportWorkedDays = report_data['worked_days']
            existing.reportTotalWeeklyOff = report_data['total_weekly_off']
            existing.reportHolidays = report_data['holidays']
            existing.reportLeavesTaken = report_data['leaves_taken']
            existing.reportLeaveDetails = leave_details_json
            existing.reportOnTimeEntries = report_data['on_time_entries']
            existing.reportEarlyOut = report_data['early_out']
            existing.reportLateIn = report_data['late_in']
            existing.reportAbsentDays = report_data['absent_days']
        else:
            existing = MonthlyReport(
                reportUserId=user_id, reportMonth=month, reportYear=year,
                reportTotalWorkingHours=report_data['total_working_hours'],
                reportWorkedDays=report_data['worked_days'],
                reportTotalWeeklyOff=report_data['total_weekly_off'],
                reportHolidays=report_data['holidays'],
                reportLeavesTaken=report_data['leaves_taken'],
                reportLeaveDetails=leave_details_json,
                reportOnTimeEntries=report_data['on_time_entries'],
                reportEarlyOut=report_data['early_out'],
                reportLateIn=report_data['late_in'],
                reportAbsentDays=report_data['absent_days']
            )
            db.session.add(existing)
        db.session.commit()
        return jsonify({"success": True, "report": report_data})
    
    @app.route("/api/monthly-reports", methods=["GET"])
    def api_get_monthly_reports():
        """
        Get Saved Monthly Reports
        ---
        tags:
          - Reports
        parameters:
          - name: user_id
            in: query
            type: integer
            description: Filter by user ID
          - name: year
            in: query
            type: integer
            description: Filter by year
        responses:
          200:
            description: List of saved monthly reports
        """
        user_id = request.args.get('user_id', type=int)
        year = request.args.get('year', type=int)
        query = MonthlyReport.query
        if user_id:
            query = query.filter_by(reportUserId=user_id)
        if year:
            query = query.filter_by(reportYear=year)
        reports = query.order_by(MonthlyReport.reportYear.desc(), MonthlyReport.reportMonth.desc()).all()
        return jsonify({"success": True, "reports": [r.to_dict() for r in reports]})
    
    @app.route("/monthly-reports")
    def monthly_reports_view():
        return render_template("monthly_reports.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
