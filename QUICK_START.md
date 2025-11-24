# Quick Start Guide - Clock In/Out System

## Step 1: Configure Your Office Location

Open `config.py` and update these values:

```python
# Get your office coordinates from Google Maps
# Right-click on your office location -> Click coordinates to copy
OFFICE_LATITUDE = 28.6139  # Replace with YOUR latitude
OFFICE_LONGITUDE = 77.2090  # Replace with YOUR longitude

# Set how close users must be (in meters)
GEOFENCE_RADIUS_METERS = 2  # Recommended: 10-50 for real GPS accuracy

# Add your office IP addresses
ALLOWED_IPS = [
    "127.0.0.1",      # For local testing
    "localhost",       # For local testing
    # Add your office IPs below:
    # "203.0.113.45",  # Example office IP
]
```

## Step 2: Run Migration (If Updating Existing Database)

```bash
python migrate_db.py
```

You should see:
```
Running 6 migrations...
[SUCCESS] Migration completed successfully!
```

## Step 3: Start the Application

```bash
python app.py
```

## Step 4: Test the System

1. **Register a User**:
   - Go to http://127.0.0.1:5000/register
   - Enter name, employee code, and upload face photo
   - Click "Register"

2. **Clock In**:
   - Go to "Clock In/Out" in the menu
   - Allow camera and location permissions
   - Click "Clock In" button
   - You should see: "Clocked in at HH:MM:SS"

3. **Clock Out**:
   - Click "Clock Out" button
   - You should see: "Clocked out at HH:MM:SS"

4. **View Report**:
   - Go to "Report" in the menu
   - See clock-in/out times, duration, location, and IP

## Important Notes

### For Development/Testing:
- Keep `ALLOWED_IPS = ["127.0.0.1", "localhost"]`
- Set `GEOFENCE_RADIUS_METERS = 1000` (large radius for testing)
- Use your actual coordinates or test coordinates

### For Production:
- Add your office's public IP to `ALLOWED_IPS`
- Set `GEOFENCE_RADIUS_METERS = 10` to `50` (GPS accuracy is 5-10m)
- Use exact office coordinates
- Enable HTTPS (required for geolocation in production)

### Getting Your Office Coordinates:
1. Open Google Maps
2. Search for your office
3. Right-click on the location
4. Click on the coordinates (they'll be copied)
5. Paste into `config.py`

### Getting Your IP Address:
- Visit: https://whatismyipaddress.com/
- Copy your IPv4 address
- Add to `ALLOWED_IPS` in `config.py`

## Troubleshooting

### "Location access denied"
- Browser blocked location access
- Click the lock icon in address bar
- Allow location permissions
- Refresh the page

### "IP not allowed"
- Your IP is not in the whitelist
- Add your current IP to `ALLOWED_IPS` in `config.py`
- Restart the application

### "You are Xm away from office"
- You're outside the geofence radius
- For testing: Increase `GEOFENCE_RADIUS_METERS` to 1000
- For production: Ensure coordinates are correct

### "Already clocked in"
- You've already clocked in today
- Clock out first, then you can clock in again tomorrow

### "No face detected"
- Ensure good lighting
- Face the camera directly
- Remove glasses/mask if needed
- Try again

## Features Overview

✓ Face recognition for authentication
✓ GPS location tracking (2m geofence)
✓ IP address validation
✓ Clock-in and clock-out timestamps
✓ Work duration calculation
✓ Attendance reports with location and IP
✓ Prevents duplicate clock-ins
✓ Audit trail for all attendance

## Support

For detailed documentation, see:
- `CLOCK_FEATURES.md` - Feature details
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `README.md` - General information
