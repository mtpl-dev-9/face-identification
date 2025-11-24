# Clock In/Out Features

## New Features Added

### 1. Clock In/Out System
- Separate clock-in and clock-out actions
- Records exact time for both actions
- Prevents duplicate clock-ins without clock-out
- Shows duration between clock-in and clock-out

### 2. Location Tracking (Geofencing)
- Uses browser's GPS to get user location
- Validates user is within 2 meters of office location
- Records latitude/longitude with each attendance
- Rejects attendance if outside geofence radius

### 3. IP Address Restriction
- Records IP address with each attendance
- Validates against whitelist of allowed IPs
- Blocks attendance from unauthorized IPs
- Supports X-Forwarded-For header for proxy setups

### 4. Attendance Report
- Shows clock-in and clock-out times
- Calculates work duration
- Displays location coordinates
- Shows IP address used
- Color-coded badges for easy reading

## Configuration

Edit `config.py` to set your office location and allowed IPs:

```python
# Office location (replace with your coordinates)
OFFICE_LATITUDE = 28.6139  # Your office latitude
OFFICE_LONGITUDE = 77.2090  # Your office longitude
GEOFENCE_RADIUS_METERS = 2  # Radius in meters

# Allowed IP addresses
ALLOWED_IPS = ["127.0.0.1", "localhost", "YOUR_OFFICE_IP"]
```

## Setup Instructions

1. **Update Configuration**
   - Open `config.py`
   - Set `OFFICE_LATITUDE` and `OFFICE_LONGITUDE` to your office coordinates
   - Add your office IP addresses to `ALLOWED_IPS` list

2. **Migrate Database** (if you have existing database)
   ```bash
   python migrate_db.py
   ```

3. **Run Application**
   ```bash
   python app.py
   ```

4. **Access Clock In/Out**
   - Navigate to "Clock In/Out" in the menu
   - Allow camera and location permissions
   - Click "Clock In" to start work
   - Click "Clock Out" to end work

## How It Works

### Clock In Process:
1. User opens Clock In/Out page
2. Browser requests camera and location permissions
3. User clicks "Clock In" button
4. System captures face image
5. System validates:
   - IP address is in whitelist
   - Location is within 2m of office
   - Face matches registered person
   - User hasn't already clocked in
6. Records clock-in time, location, and IP
7. Shows success message

### Clock Out Process:
1. User clicks "Clock Out" button
2. System validates same as clock-in
3. Checks user has clocked in today
4. Records clock-out time
5. Calculates work duration
6. Shows success message

## API Endpoints

### POST /api/attendance/clock
Clock in or clock out with face recognition and location validation

**Request:**
```json
{
  "image": "data:image/jpeg;base64,...",
  "action": "clock_in",  // or "clock_out"
  "latitude": 28.6139,
  "longitude": 77.2090
}
```

**Response (Success):**
```json
{
  "success": true,
  "person": {...},
  "attendance": {...},
  "message": "Clocked in at 09:30:15",
  "distance_from_office": 1.5
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "You are 5.2m away. Must be within 2m"
}
```

## Security Features

1. **Geofencing**: Ensures employees are physically at office
2. **IP Whitelisting**: Prevents remote attendance marking
3. **Face Recognition**: Prevents proxy attendance
4. **Duplicate Prevention**: Can't clock in twice without clock out
5. **Audit Trail**: Records location and IP for every attendance

## Troubleshooting

### Location Not Working
- Ensure HTTPS is enabled (required for geolocation API)
- Check browser permissions for location access
- For local testing, use `localhost` (not 127.0.0.1)

### IP Restriction Issues
- Add your current IP to `ALLOWED_IPS` in config.py
- For development, keep "127.0.0.1" and "localhost"
- For production, add your office's public IP

### Geofence Too Strict
- Increase `GEOFENCE_RADIUS_METERS` in config.py
- Note: GPS accuracy is typically 5-10 meters
- Consider setting radius to at least 10 meters for reliability

## Getting Office Coordinates

1. Go to Google Maps
2. Right-click on your office location
3. Click on the coordinates to copy them
4. Update `OFFICE_LATITUDE` and `OFFICE_LONGITUDE` in config.py
