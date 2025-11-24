# Advanced Face Recognition Attendance System (Flask)

This is a complete, advanced-level face-recognition-based attendance system built with:

- Python 3
- Flask
- face_recognition (dlib)
- OpenCV (only on server side for image handling)
- SQLite + SQLAlchemy

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

1. Create venv and install deps:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

> Note: `face-recognition` may require build tools (CMake, etc.). On Windows you might prefer installing a prebuilt Python/Anaconda or precompiled wheels.

2. Configure office location and IP whitelist in `config.py`:

```python
OFFICE_LATITUDE = 28.6139  # Your office latitude
OFFICE_LONGITUDE = 77.2090  # Your office longitude
GEOFENCE_RADIUS_METERS = 2  # 2 meters
ALLOWED_IPS = ["127.0.0.1", "YOUR_OFFICE_IP"]
```

3. Run database migration (if updating existing database):

```bash
python migrate_db.py
```

4. Run:

```bash
python app.py
```

5. Open `http://127.0.0.1:5000` in browser.

## Usage

1. Go to **Register** and add people (name, employee code, face image).

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
