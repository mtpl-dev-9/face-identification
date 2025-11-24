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
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "attendance.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    FACE_RECOGNITION_TOLERANCE = 0.5  # lower = stricter
    
    # Location-based attendance settings
    OFFICE_LATITUDE = 23.022797   # Replace with your office latitude
    OFFICE_LONGITUDE =   72.531968  # Replace with your office longitude
    GEOFENCE_RADIUS_METERS = 10000  # 10km for testing (change to 50 for production)
    
    # IP whitelist (add your allowed IPs)
    ALLOWED_IPS = ["127.0.0.1", "localhost"]  # Add your office IPs here
