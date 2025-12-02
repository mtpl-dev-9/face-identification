import os
from datetime import datetime, timedelta
from typing import List

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

from config import Config, calculate_distance, IST
from database import db
from models import Person, Attendance, Settings, AllowedIP, Holiday, User
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
)
import face_recognition


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

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

    # ---------- helper: match face ----------
    def match_single_encoding(encoding):
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
           user_id = data.get("user_id")
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

           # Check if user already has biometric (allow update if exists)
           existing_person = Person.query.filter_by(biometricUserId=user_id_int).first()
           if existing_person:
               # Delete old biometric for update
               db.session.delete(existing_person)
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
        """Delete user's biometric data"""
        try:
            person = Person.query.filter_by(biometricUserId=user_id).first()
            if not person:
                return jsonify({"success": False, "error": "No biometric found"}), 404
            
            db.session.delete(person)
            db.session.commit()
            
            return jsonify({"success": True, "message": "Biometric deleted successfully"})
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
                user_id:
                  type: integer
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

        if not user_id or not image_data or not action:
            return jsonify({"success": False, "error": "user_id, image and action required"}), 400

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

        # Verify detected face matches the authenticated user
        if person.biometricUserId != user_id:
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

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
