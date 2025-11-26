import os
from math import radians, sin, cos, sqrt, atan2
import pytz

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
IST = pytz.timezone('Asia/Kolkata')

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in meters using Haversine formula"""
    R = 6371000  # Earth radius in meters
    
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    
    a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c

class Config:
    # ============================================
    # FLASK SECRET KEY CONFIGURATION
    # ============================================
    # Generate secure key: python -c "import secrets; print(secrets.token_hex(32))"
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-key-f8a3c9e2d1b4a7f6e5d4c3b2a1"
    
    # ============================================
    # DATABASE CONFIGURATION
    # ============================================
    # XAMPP MySQL Configuration (default: no password for root)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:@localhost:3306/face_attendance"
    )
    # For SQLite (comment out MySQL and uncomment below):
    # SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "instance", "attendance.db")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
    }
    
    # ============================================
    # FILE UPLOAD CONFIGURATION
    # ============================================
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size
    
    # ============================================
    # FACE RECOGNITION CONFIGURATION
    # ============================================
    FACE_RECOGNITION_TOLERANCE = 0.5  # 0.4-0.6 recommended (lower = stricter)
    
    # ============================================
    # LOCATION-BASED ATTENDANCE (Geofencing)
    # ============================================
    # These can be updated via Settings page in the web interface
    OFFICE_LATITUDE = 23.022797      # Your office latitude
    OFFICE_LONGITUDE = 72.531968     # Your office longitude
    GEOFENCE_RADIUS_METERS = 10000   # 10km for testing, use 50m for production
    
    # ============================================
    # IP WHITELIST CONFIGURATION
    # ============================================
    # Add allowed IP addresses here or manage via Settings page
    ALLOWED_IPS = [
        "127.0.0.1",           # Localhost IPv4
        "::1",                 # Localhost IPv6
        "localhost",           # Localhost hostname
        # Add your office/allowed IPs below:
        # "203.0.113.45",      # Example office IP
        # "198.51.100.0/24",   # Example IP range
    ]
