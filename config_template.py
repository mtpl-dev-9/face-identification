"""
Configuration Template for Clock In/Out System

INSTRUCTIONS:
1. Copy this file to config.py (if not already done)
2. Update the values below with your office details
3. Save the file
4. Run: python migrate_db.py
5. Run: python app.py
"""

import os
from math import radians, sin, cos, sqrt, atan2

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

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
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "attendance.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    FACE_RECOGNITION_TOLERANCE = 0.5  # lower = stricter (0.4-0.6 recommended)
    
    # ============================================================
    # LOCATION-BASED ATTENDANCE SETTINGS
    # ============================================================
    
    # TODO: Get your office coordinates from Google Maps
    # Steps:
    # 1. Open Google Maps (https://maps.google.com)
    # 2. Search for your office address
    # 3. Right-click on the location
    # 4. Click on the coordinates to copy them
    # 5. Paste below
    
    OFFICE_LATITUDE = 28.6139   # REPLACE WITH YOUR OFFICE LATITUDE
    OFFICE_LONGITUDE = 77.2090  # REPLACE WITH YOUR OFFICE LONGITUDE
    
    # Geofence radius in meters
    # Note: GPS accuracy is typically 5-10 meters
    # Recommendation:
    #   - For testing: 1000 (1 km)
    #   - For production: 10-50 meters
    #   - As requested: 2 meters (may be too strict due to GPS accuracy)
    
    GEOFENCE_RADIUS_METERS = 2  # ADJUST AS NEEDED
    
    # ============================================================
    # IP ADDRESS RESTRICTION
    # ============================================================
    
    # TODO: Add your office IP addresses
    # Steps:
    # 1. Visit https://whatismyipaddress.com/ from office network
    # 2. Copy your IPv4 address
    # 3. Add to the list below
    
    ALLOWED_IPS = [
        "127.0.0.1",      # Localhost (for development)
        "localhost",       # Localhost (for development)
        # Add your office IPs below:
        # "203.0.113.45",  # Example: Office IP 1
        # "203.0.113.46",  # Example: Office IP 2
        # "10.0.0.0/8",    # Example: Private network range (if needed)
    ]
    
    # ============================================================
    # NOTES
    # ============================================================
    
    # For Development/Testing:
    # - Keep ALLOWED_IPS = ["127.0.0.1", "localhost"]
    # - Set GEOFENCE_RADIUS_METERS = 1000 (large radius)
    # - Use any test coordinates
    
    # For Production:
    # - Add your office's public IP to ALLOWED_IPS
    # - Set GEOFENCE_RADIUS_METERS = 10 to 50
    # - Use exact office coordinates
    # - Enable HTTPS (required for geolocation)
    
    # Security Recommendations:
    # - Change SECRET_KEY to a random string
    # - Use environment variables for sensitive data
    # - Enable HTTPS in production
    # - Regularly update ALLOWED_IPS list
    # - Monitor attendance logs for anomalies
