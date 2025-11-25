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

from config import Config, calculate_distance, IST
from database import db
from models import Person, Attendance, Settings, AllowedIP
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

    with app.app_context():
        db.create_all()

    # ---------- helper: match face ----------
    def match_single_encoding(encoding):
        persons: List[Person] = Person.query.filter_by(is_active=True).all()
        if not persons:
            return None, None

        known_encodings = [decode_from_json(p.encoding) for p in persons]
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
            Attendance.timestamp >= today_start
        ).count()
        
        # Calculate absent count
        attended_person_ids = db.session.query(Attendance.person_id).filter(
            Attendance.timestamp >= today_start,
            Attendance.clock_in_time.isnot(None)
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
        now = get_ist_now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Today's stats
        today_records = Attendance.query.filter(
            Attendance.timestamp >= today_start,
            Attendance.clock_in_time.isnot(None)
        ).all()
        
        late_count = sum(1 for r in today_records if r.clock_in_time and r.clock_in_time.hour >= 10)
        overtime_count = sum(1 for r in today_records if r.clock_out_time and r.clock_out_time.hour >= 18)
        
        # Calculate absent count
        attended_person_ids = db.session.query(Attendance.person_id).filter(
            Attendance.timestamp >= today_start,
            Attendance.clock_in_time.isnot(None)
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
                Attendance.timestamp >= day,
                Attendance.timestamp < day_end,
                Attendance.clock_in_time.isnot(None)
            ).count()
            weekly_data.append({"day": day.strftime("%a"), "count": count})
        
        # Monthly data (last 30 days)
        monthly_data = []
        for i in range(30):
            day = today_start - timedelta(days=29-i)
            day_end = day + timedelta(days=1)
            count = Attendance.query.filter(
                Attendance.timestamp >= day,
                Attendance.timestamp < day_end,
                Attendance.clock_in_time.isnot(None)
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
        emp_code = request.form.get("employee_code")
        image_file = request.files.get("image")

        if not name or not emp_code or not image_file:
            flash("Name, employee code and image are required", "danger")
            return redirect(request.url)

        if Person.query.filter_by(employee_code=emp_code).first():
            flash("Employee code already exists", "danger")
            return redirect(request.url)

        img_array = load_image_from_file_storage(image_file)
        encodings = get_face_encodings(img_array)

        if not encodings:
            flash("No face found in the image. Try another photo.", "warning")
            return redirect(request.url)
        if len(encodings) > 1:
            flash("Multiple faces found. Please upload a single face photo.", "warning")
            return redirect(request.url)

        encoding_json = encode_to_json(encodings[0])
        person = Person(name=name, employee_code=emp_code, encoding=encoding_json)
        db.session.add(person)
        db.session.commit()

        flash(f"Registered {name} ({emp_code})", "success")
        return redirect(url_for("index"))
    @app.route("/api/register-face-live", methods=["POST"])
    def api_register_face_live():
       data = request.get_json() or {}

       name = data.get("name")
       emp_code = data.get("employee_code")
       image_data = data.get("image")

       if not name or not emp_code or not image_data:
           return jsonify({"success": False, "error": "All fields required"}), 400

       if Person.query.filter_by(employee_code=emp_code).first():
           return jsonify({"success": False, "error": "Employee code already exists"}), 400

       img_array = load_image_from_base64(image_data)
       encodings = get_face_encodings(img_array)

       if not encodings:
           return jsonify({"success": False, "error": "No face detected"}), 422
       if len(encodings) > 1:
           return jsonify({"success": False, "error": "Multiple faces detected"}), 422

       encoding_json = encode_to_json(encodings[0])
       person = Person(name=name, employee_code=emp_code, encoding=encoding_json)
       db.session.add(person)
       db.session.commit()

       return jsonify({"success": True, "person": person.to_dict()})

    # --- people list ---
    @app.route("/persons")
    def persons_view():
        persons = Person.query.order_by(Person.created_at.desc()).all()
        return render_template("persons.html", persons=persons)

    @app.route("/api/persons/<int:person_id>", methods=["DELETE", "POST"])
    def api_delete_person(person_id):
        try:
            person = Person.query.get(person_id)
            if not person:
                return jsonify({"success": False, "error": "Person not found"}), 404
            
            # Delete associated attendance records first
            Attendance.query.filter_by(person_id=person_id).delete()
            
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
        records = Attendance.query.order_by(Attendance.timestamp.desc()).limit(100).all()
        return render_template("attendance.html", records=records)

    @app.route("/attendance/report")
    def attendance_report_view():
        records = Attendance.query.order_by(Attendance.timestamp.desc()).limit(100).all()
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
        return jsonify(get_office_settings())

    @app.route("/api/settings", methods=["POST"])
    def api_update_settings():
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

    @app.route("/api/register-face", methods=["POST"])
    def api_register_face():
        name = request.form.get("name")
        emp_code = request.form.get("employee_code")
        image_file = request.files.get("image")

        if not name or not emp_code or not image_file:
            return jsonify({"success": False, "error": "name, employee_code, image required"}), 400

        if Person.query.filter_by(employee_code=emp_code).first():
            return jsonify({"success": False, "error": "employee_code exists"}), 400

        img_array = load_image_from_file_storage(image_file)
        encodings = get_face_encodings(img_array)

        if not encodings:
            return jsonify({"success": False, "error": "no face found"}), 422
        if len(encodings) > 1:
            return jsonify({"success": False, "error": "multiple faces found"}), 422

        encoding_json = encode_to_json(encodings[0])
        person = Person(name=name, employee_code=emp_code, encoding=encoding_json)
        db.session.add(person)
        db.session.commit()

        return jsonify({"success": True, "person": person.to_dict()})

    @app.route("/api/attendance/clock", methods=["POST"])
    def api_attendance_clock():
        data = request.get_json(silent=True) or {}
        image_data = data.get("image")
        action = data.get("action")
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if not image_data or not action:
            return jsonify({"success": False, "error": "image and action required"}), 400

        if action not in ["clock_in", "clock_out"]:
            return jsonify({"success": False, "error": "action must be clock_in or clock_out"}), 400

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

        img_array = load_image_from_base64(image_data)
        encodings = get_face_encodings(img_array)

        if not encodings:
            return jsonify({"success": False, "error": "No face detected"}), 422

        encoding = encodings[0]
        person, face_distance = match_single_encoding(encoding)

        if not person:
            return jsonify({"success": False, "error": "Unknown face"}), 404

        now = get_ist_now()
        today = now.date()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        today_record = Attendance.query.filter(
            and_(
                Attendance.person_id == person.id,
                Attendance.timestamp >= today_start
            )
        ).order_by(Attendance.timestamp.desc()).first()

        if action == "clock_in":
            if today_record and today_record.action == "clock_in" and not today_record.clock_out_time:
                return jsonify({"success": False, "error": "Already clocked in. Clock out first"}), 400

            record = Attendance(
                person_id=person.id,
                status="present",
                source="live_camera",
                action="clock_in",
                latitude=latitude,
                longitude=longitude,
                ip_address=client_ip,
                clock_in_time=now,
                timestamp=now
            )
            db.session.add(record)
            db.session.commit()
            message = f"Clocked in at {now.strftime('%H:%M:%S')}"

        else:
            if not today_record or today_record.action != "clock_in":
                return jsonify({"success": False, "error": "No clock-in found. Clock in first"}), 400

            if today_record.clock_out_time:
                return jsonify({"success": False, "error": "Already clocked out today"}), 400

            today_record.clock_out_time = now
            today_record.action = "clock_out"
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
        last = Attendance.query.filter_by(person_id=person.id).order_by(Attendance.timestamp.desc()).first()
        if not last or (now - last.timestamp) > timedelta(minutes=1):
            record = Attendance(person_id=person.id, status="present", source="live_camera")
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
        records = Attendance.query.order_by(Attendance.timestamp.desc()).limit(20).all()
        return jsonify(
            {
                "success": True,
                "results": [r.to_dict() for r in records],
            }
        )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
