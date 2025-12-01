# Advanced Face Recognition Attendance System (Flask)

A complete, production-ready face-recognition-based attendance system with geofencing, IP restrictions, break management, and holiday tracking.

## Tech Stack

- **Backend**: Python 3, Flask, SQLAlchemy
- **Face Recognition**: face_recognition (dlib), OpenCV
- **Database**: MySQL / SQLite
- **Frontend**: Bootstrap 5, JavaScript, Chart.js
- **API Documentation**: Swagger/OpenAPI (Flasgger)
- **Timezone**: Indian Standard Time (IST)

## Features

### 👤 Person Management
- Register employees with name, employee code, and face image
- Face encoding storage in database
- Delete persons with cascade deletion of attendance records
- Active/inactive status management

### ⏰ Clock In/Out System
- **Face recognition** for secure authentication
- **Geofencing** with configurable radius (default 10km for testing, 50m for production)
- **IP address whitelist** validation
- Records exact clock-in and clock-out times (IST)
- **Break In/Out** tracking without face recognition
- Automatic work duration calculation (excludes break time)
- Prevents duplicate clock-ins
- Location coordinates stored with each entry

### 📊 Analytics Dashboard
- **Today's Statistics**: Total present, absent, late arrivals (≥10 AM), overtime (≥6 PM)
- **Weekly Chart**: Bar chart showing attendance for last 7 days
- **Monthly Chart**: Line chart showing attendance for last 30 days
- Auto-refresh every 60 seconds
- Real-time absent count calculation

### 📅 Holiday Management
- **Manual Date Selection**: Add specific holidays (e.g., Diwali, Christmas)
- **Weekly Pattern Mode**: Select weekdays and weeks to apply holidays
  - Choose specific days (Monday-Sunday)
  - Choose specific weeks (1st, 2nd, 3rd, 4th, 5th)
  - Bulk apply to entire month
- Calendar view with color coding:
  - 🔴 Red = Holiday
  - 🟡 Yellow = Week-Off
  - 🟢 Green = Working Day
  - ⚫ Dark Gray = Sunday
- Holiday list with delete functionality

### 🏖️ Leave Management System (NEW)
- **Dynamic Leave Types**: Create unlimited leave types (Casual, Sick, Celebratory, etc.)
- **Admin Controls**:
  - Create/manage leave types dynamically
  - Assign leave balances to employees
  - Set year-wise leave quotas
  - Approve/reject leave requests
- **Employee Features**:
  - View leave balance (total, used, remaining)
  - Request leaves with date range
  - Track request status (pending/approved/rejected)
  - Add reason/notes for leave
- **Smart Validation**:
  - Automatic leave days calculation
  - Balance verification before approval
  - Prevents over-allocation
  - Year-wise tracking
- **Approval Workflow**:
  - Pending → Approved/Rejected flow
  - Automatic balance deduction on approval
  - Tracks approver and timestamp

### 🔧 Settings Management
- **Office Location**: Configure latitude/longitude via web UI
- **Geofence Radius**: Adjustable radius in meters
- **IP Whitelist**: Manage allowed IP addresses
- Database-driven configuration (no code changes needed)

### 📱 Live Attendance
- Browser-based webcam access
- Real-time face recognition
- Automatic attendance marking
- Live-updating attendance sidebar
- Duplicate prevention (1 minute window)

### 📄 Reports
- **Attendance Report**: Clock in/out times, break times, work duration, location, IP
- **Attendance Log**: Complete history with timestamps
- Export-ready data format

### 🔐 Security Features
- IP address validation and logging
- Geofencing with Haversine formula
- Face recognition tolerance configuration
- CORS enabled for API access
- Secure secret key configuration

## Project Structure

```
face_a/
├── app.py                      # Main Flask application
├── config.py                   # Configuration (DB, geofencing, IP whitelist)
├── database.py                 # SQLAlchemy instance
├── models.py                   # Database models (Person, Attendance, Holiday, Settings)
├── face_utils.py               # Face recognition utilities
├── swagger_config.py           # Swagger/OpenAPI configuration
├── swagger_docs.py             # API documentation specs
├── requirements.txt            # Python dependencies
├── templates/                  # HTML templates
│   ├── base.html              # Base template with navbar
│   ├── index.html             # Dashboard with analytics
│   ├── register.html          # Person registration
│   ├── persons.html           # Person list
│   ├── clock_attendance.html  # Clock in/out page
│   ├── attendance_report.html # Attendance report
│   ├── holidays.html          # Holiday management
│   ├── leave_management.html  # Leave management (NEW)
│   └── settings.html          # Settings page
├── static/
│   ├── css/main.css           # Custom styles with animations
│   └── js/main.js             # Webcam and attendance logic
├── instance/                   # SQLite database (if not using MySQL)
├── uploads/                    # Uploaded face images
├── API_DOCUMENTATION.md        # Complete API reference
├── API_QUICK_REFERENCE.md      # Quick start guide
├── DATABASE_DOCUMENTATION.md   # Database schema docs
├── DATABASE_SCHEMA.sql         # SQL schema file
├── SWAGGER_SETUP.md            # Swagger setup guide
├── leave_management_schema.sql # Leave system SQL schema (NEW)
├── LEAVE_MANAGEMENT_GUIDE.md   # Leave system guide (NEW)
├── init_leave_system.py        # Leave system initializer (NEW)
└── README.md                   # This file
```

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

3. Generate secure secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Update in `config.py`.

4. Initialize Leave Management System (NEW):

```bash
# Run SQL schema
mysql -u root -p mtpl_website < leave_management_schema.sql

# Or initialize via Python script
python init_leave_system.py
```

5. Run the application:

```bash
python app.py
```

6. Access the application:

- **Web UI**: http://127.0.0.1:5000
- **Leave Management**: http://127.0.0.1:5000/leave-management (NEW)
- **Swagger API Docs**: http://127.0.0.1:5000/api/docs
- **API Spec JSON**: http://127.0.0.1:5000/apispec.json

## API Documentation

### Interactive Swagger UI
Access interactive API documentation at:
- **http://127.0.0.1:5000/api/docs**

### Available API Endpoints

**Analytics**
- `GET /api/analytics/dashboard` - Dashboard statistics

**Attendance**
- `POST /api/attendance/clock` - Clock in/out with face recognition
- `POST /api/attendance/break` - Break in/out
- `GET /api/attendance/latest` - Get latest 20 records

**Holidays**
- `GET /api/holidays` - Get holidays for month
- `POST /api/holidays` - Add new holiday
- `DELETE /api/holidays/{id}` - Delete holiday

**Settings**
- `GET /api/settings` - Get office settings
- `POST /api/settings` - Update office settings

**Person Management**
- `POST /api/register-face` - Register new person
- `DELETE /api/persons/{id}` - Delete person

**Leave Management (NEW)**
- `GET /api/leave-types` - Get all leave types
- `POST /api/leave-types` - Create leave type
- `DELETE /api/leave-types/{id}` - Delete leave type
- `GET /api/user-leave-balance` - Get user leave balance
- `POST /api/user-leave-balance` - Assign leave balance
- `GET /api/leave-requests` - Get leave requests
- `POST /api/leave-requests` - Create leave request
- `POST /api/leave-requests/{id}/approve` - Approve request
- `POST /api/leave-requests/{id}/reject` - Reject request

### Documentation Files
- `API_DOCUMENTATION.md` - Complete API reference with examples
- `API_QUICK_REFERENCE.md` - Quick start guide
- `SWAGGER_SETUP.md` - Swagger setup and usage guide
- `DATABASE_DOCUMENTATION.md` - Database schema and queries
- `LEAVE_MANAGEMENT_GUIDE.md` - Leave system complete guide (NEW)

## Usage

### 1. Register Employees
- Navigate to **Register** page
- Enter name and employee code
- Upload face image (single face, clear photo)
- System extracts and stores face encoding

### 2. Clock In/Out (Recommended)
- Go to **Clock In/Out** page
- Allow camera and location access
- Click **Clock In** to start work
  - System validates face, location, and IP
  - Records clock-in time and location
- Click **Break In/Out** for breaks (no face recognition needed)
- Click **Clock Out** to end work
  - Calculates total work duration minus break time

### 3. Manage Holidays
- Go to **Holidays** page
- **Manual Mode**: Select specific date and add holiday
- **Weekly Pattern Mode**: 
  - Select weekdays (e.g., Saturday, Sunday)
  - Select weeks (e.g., 2nd, 4th)
  - Apply to entire month
- View calendar with color-coded days

### 4. Configure Settings
- Go to **Settings** page
- Update office location (latitude/longitude)
- Adjust geofence radius
- Manage IP whitelist
- Changes saved to database immediately

### 5. View Analytics
- **Dashboard**: Real-time stats with charts
- **Attendance Report**: Detailed records with times and locations
- **Persons**: List of registered employees

### 6. Manage Leaves (NEW)
- Go to **Leave Management** page
- **Admin Panel**:
  - Create leave types (Casual, Sick, Celebratory)
  - Assign leave balances to employees
  - Set total leaves per year
- **Employee Panel**:
  - View leave balance
  - Request leaves with date range
  - Track request status
- **Leave Requests**:
  - View all requests
  - Filter by status
  - Approve/reject requests

### 7. API Integration
- Access Swagger UI at `/api/docs`
- Test APIs directly in browser
- Export to Postman via `/apispec.json`
- Use cURL commands from Swagger UI

## Database Structure

### Tables

**person**
- `id`, `name`, `employee_code`, `encoding` (face data), `is_active`, `created_at`

**attendance**
- `id`, `person_id`, `timestamp`, `status`, `source`
- `clock_in_time`, `clock_out_time`, `break_in_time`, `break_out_time`
- `latitude`, `longitude`, `ip_address`, `action`

**holiday**
- `id`, `date`, `name`, `is_weekoff`, `created_at`

**settings**
- `id`, `key`, `value`, `updated_at`
- Stores: `office_latitude`, `office_longitude`, `geofence_radius`

**allowed_ip**
- `id`, `ip_address`, `description`, `is_active`, `created_at`

**leave_types (NEW)**
- `id`, `name`, `is_active`, `created_at`

**user_leave_balance (NEW)**
- `id`, `user_id`, `leave_type_id`, `total`, `used`, `year`, `updated_at`

**leave_requests (NEW)**
- `id`, `user_id`, `leave_type_id`, `from_date`, `to_date`, `days`, `reason`
- `status`, `approved_by`, `approved_at`, `created_at`

### Database Configuration

Supports both MySQL and SQLite:

**MySQL** (Production):
```python
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://user:pass@localhost:3306/dbname"
```

**SQLite** (Development):
```python
SQLALCHEMY_DATABASE_URI = "sqlite:///instance/attendance.db"
```

See `DATABASE_DOCUMENTATION.md` for complete schema and sample queries.

## Configuration

### Flask Secret Key

Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Update in `config.py` or set environment variable:
```bash
export SECRET_KEY="your-generated-key"
```

### Office Location

Update in `config.py` or via Settings page:
```python
OFFICE_LATITUDE = 23.022797    # Your office latitude
OFFICE_LONGITUDE = 72.531968   # Your office longitude
GEOFENCE_RADIUS_METERS = 50    # 50m for production
```

### IP Whitelist

Add allowed IPs in `config.py` or via Settings page:
```python
ALLOWED_IPS = [
    "127.0.0.1",
    "::1",
    "YOUR_OFFICE_IP"
]
```

### Face Recognition Tolerance

Adjust in `config.py` (0.4-0.6 recommended):
```python
FACE_RECOGNITION_TOLERANCE = 0.5  # Lower = stricter
```

## Production Deployment

1. **Set secure secret key**
2. **Use MySQL database**
3. **Update geofence radius to 50m**
4. **Add production IPs to whitelist**
5. **Enable HTTPS**
6. **Use production WSGI server** (Gunicorn/uWSGI)
7. **Update Swagger host** in `swagger_config.py`

```bash
# Example with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Troubleshooting

### Face Recognition Installation Issues

Windows users may need Visual Studio Build Tools:
- Download from: https://visualstudio.microsoft.com/downloads/
- Or use precompiled wheels: https://github.com/ageitgey/face_recognition

### Database Connection Issues

Check MySQL connection:
```bash
mysql -u root -p
CREATE DATABASE attendance_db;
```

### Geofencing Not Working

Ensure browser has location permissions and HTTPS is enabled (required for geolocation API).

### IP Validation Failing

Add your IP to whitelist via Settings page or `config.py`.

## License

MIT License - See LICENSE file for details.

## Support

For issues and questions:
- Check `SWAGGER_SETUP.md` for API documentation
- Check `DATABASE_DOCUMENTATION.md` for database queries
- Review `API_DOCUMENTATION.md` for integration examples
- Read `LEAVE_MANAGEMENT_GUIDE.md` for leave system usage
