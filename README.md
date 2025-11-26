# Advanced Face Recognition Attendance System (Flask)

This is a complete, advanced-level face-recognition-based attendance system built with:

- Python 3
- Flask
- face_recognition (dlib)
- OpenCV (only on server side for image handling)
- MySQL + SQLAlchemy (MTPL Database Integration)

## Features

- Register persons with **name + employee code + face image**
- Store face encodings in database
- **Clock In/Out System**:
  - Face recognition for clock in/out
  - **Location tracking with 2m geofencing**
  - **IP address restriction and validation**
  - Records exact clock-in and clock-out times
  - Calculates work duration
  - Prevents duplicate clock-ins
- Live camera attendance page:
  - Browser uses webcam (getUserMedia)
  - Periodically sends frames to backend
  - Backend recognizes faces and **logs attendance with timestamp**
  - Duplicate prevention window (1 minute per person)
- Simple dashboards:
  - Overview (counts)
  - Persons list
  - Recent attendance log
  - **Attendance report with clock times, location, and IP**
  - Live attendance page with:
    - Live camera
    - Live-updating attendance sidebar

## Project structure

- `app.py` – main Flask app and routes
- `config.py` – configuration (DB, paths, tolerance)
- `database.py` – SQLAlchemy instance
- `models.py` – `Person` and `Attendance` models
- `face_utils.py` – helpers to handle images and encodings
- `templates/` – HTML pages (Bootstrap)
- `static/js/main.js` – webcam + live attendance logic
- `static/css/main.css` – basic styling

## Setup

1. Install Python dependencies:

```bash
pip install flask flask-cors flask-sqlalchemy pymysql cryptography face-recognition opencv-python pillow numpy flasgger pytz
```

Or use requirements.txt:

```bash
pip install -r requirements.txt
```

> Note: `face-recognition` requires CMake and dlib. On Windows, install Visual Studio Build Tools or use precompiled wheels from https://github.com/ageitgey/face_recognition

2. Configure MySQL database in `config.py`:

```python
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost:3306/mtpl_website"
OFFICE_LATITUDE = 28.6139  # Your office latitude
OFFICE_LONGITUDE = 77.2090  # Your office longitude
GEOFENCE_RADIUS_METERS = 2  # 2 meters
ALLOWED_IPS = ["127.0.0.1", "YOUR_OFFICE_IP"]
```

3. Run:

```bash
python app.py
```

5. Open `http://127.0.0.1:5000` in browser.

## API Documentation

Interactive Swagger API documentation available at:
- **http://127.0.0.1:5000/api/docs**

Detailed API documentation:
- `API_DOCUMENTATION.md` - Complete API reference
- `API_QUICK_REFERENCE.md` - Quick start guide

## Usage

1. Go to **Register** and add people (name, numeric user ID, face image).

2. **Clock In/Out** (Recommended):
   - Go to **Clock In/Out** page
   - Allow camera and location access
   - Click **Clock In** to start work
   - Click **Clock Out** to end work
   - System validates:
     - Face recognition
     - Location within 2m of office
     - IP address whitelist

3. **Live Attendance** (Alternative):
   - Go to **Live Attendance**
   - Allow camera access
   - System will automatically:
     - capture frames every few seconds
     - recognize faces
     - insert attendance entries

4. View reports:
   - **Report**: Clock in/out times with location and IP
   - **Attendance Log**: All attendance records
   - **Analytics Dashboard**: Today's stats, weekly and monthly trends

## Database Structure

Integrated with MTPL database (`mtpl_website`):
- `mtpl_biometric` - Face encodings and user mappings
- `mtpl_attendance` - Attendance records with clock in/out times
- `mtpl_users` - User information (optional integration)
- `mtpl_holidays` - Holiday calendar
- `mtpl_allowed_ips` - IP whitelist
- `mtpl_attendance_settings` - System settings
