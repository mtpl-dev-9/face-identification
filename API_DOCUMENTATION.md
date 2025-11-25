# Face Attendance System - API Documentation

## Base URL
```
http://127.0.0.1:5000
```

## Authentication
- IP-based whitelist authentication
- Configure allowed IPs in Settings or database

---

## 📋 Table of Contents
1. [Person Management](#person-management)
2. [Attendance Operations](#attendance-operations)
3. [Analytics & Reports](#analytics--reports)
4. [Settings Management](#settings-management)

---

## Person Management

### 1. Register Person (Live Camera)
Register a new person with face encoding from base64 image.

**Endpoint:** `POST /api/register-face-live`

**Request Body:**
```json
{
  "name": "John Doe",
  "employee_code": "EMP001",
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

**Response (Success):**
```json
{
  "success": true,
  "person": {
    "id": 1,
    "name": "John Doe",
    "employee_code": "EMP001",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00+05:30"
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "No face detected"
}
```

**Status Codes:**
- `200` - Success
- `400` - Missing required fields
- `422` - No face or multiple faces detected

---

### 2. Register Person (File Upload)
Register a new person with face encoding from file upload.

**Endpoint:** `POST /api/register-face`

**Request:** `multipart/form-data`
- `name` (string, required)
- `employee_code` (string, required)
- `image` (file, required)

**Response:**
```json
{
  "success": true,
  "person": {
    "id": 1,
    "name": "John Doe",
    "employee_code": "EMP001",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00+05:30"
  }
}
```

---

### 3. Delete Person
Delete a registered person and all associated attendance records.

**Endpoint:** `DELETE /api/persons/{person_id}`

**Response:**
```json
{
  "success": true,
  "message": "Person deleted successfully"
}
```

**Status Codes:**
- `200` - Success
- `404` - Person not found
- `500` - Server error

---

## Attendance Operations

### 4. Clock In/Out
Mark attendance with face recognition, location, and IP validation.

**Endpoint:** `POST /api/attendance/clock`

**Request Body:**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "action": "clock_in",
  "latitude": 23.022797,
  "longitude": 72.531968
}
```

**Parameters:**
- `image` (string, required) - Base64 encoded image
- `action` (string, required) - Either "clock_in" or "clock_out"
- `latitude` (number, required) - User's latitude
- `longitude` (number, required) - User's longitude

**Response (Success):**
```json
{
  "success": true,
  "person": {
    "id": 1,
    "name": "John Doe",
    "employee_code": "EMP001"
  },
  "attendance": {
    "id": 10,
    "person_id": 1,
    "action": "clock_in",
    "clock_in_time": "2024-01-15T09:30:00+05:30",
    "latitude": 23.022797,
    "longitude": 72.531968,
    "ip_address": "192.168.1.100",
    "timestamp": "2024-01-15T09:30:00+05:30"
  },
  "message": "Clocked in at 09:30:00",
  "distance_from_office": 5.2
}
```

**Response (Error - Location):**
```json
{
  "success": false,
  "error": "You are 150.50m away. Must be within 10000m"
}
```

**Response (Error - IP):**
```json
{
  "success": false,
  "error": "Access denied. IP 192.168.1.200 not allowed"
}
```

**Status Codes:**
- `200` - Success
- `400` - Missing fields or already clocked in/out
- `403` - Location or IP validation failed
- `404` - Unknown face
- `422` - No face detected

---

### 5. Live Attendance Mark
Mark attendance from live camera (legacy method).

**Endpoint:** `POST /api/attendance/live-mark`

**Request Body:**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

**Response:**
```json
{
  "success": true,
  "match": true,
  "person": {
    "id": 1,
    "name": "John Doe",
    "employee_code": "EMP001"
  },
  "distance": 0.35,
  "attendance": {
    "id": 10,
    "person_id": 1,
    "status": "present",
    "source": "live_camera",
    "timestamp": "2024-01-15T09:30:00+05:30"
  }
}
```

**Note:** Prevents duplicate entries within 1 minute per person.

---

### 6. Get Latest Attendance
Retrieve the 20 most recent attendance records.

**Endpoint:** `GET /api/attendance/latest`

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "id": 10,
      "person_id": 1,
      "person_name": "John Doe",
      "employee_code": "EMP001",
      "action": "clock_in",
      "clock_in_time": "2024-01-15T09:30:00+05:30",
      "clock_out_time": null,
      "latitude": 23.022797,
      "longitude": 72.531968,
      "ip_address": "192.168.1.100",
      "timestamp": "2024-01-15T09:30:00+05:30"
    }
  ]
}
```

---

## Analytics & Reports

### 7. Dashboard Analytics
Get comprehensive analytics including today's stats, weekly, and monthly trends.

**Endpoint:** `GET /api/analytics/dashboard`

**Response:**
```json
{
  "today": {
    "total": 25,
    "late": 3,
    "overtime": 8,
    "ontime": 22,
    "absent": 5
  },
  "weekly": [
    {"day": "Mon", "count": 28},
    {"day": "Tue", "count": 30},
    {"day": "Wed", "count": 25},
    {"day": "Thu", "count": 27},
    {"day": "Fri", "count": 29},
    {"day": "Sat", "count": 15},
    {"day": "Sun", "count": 0}
  ],
  "monthly": [
    {"date": "01", "count": 28},
    {"date": "02", "count": 30},
    ...
    {"date": "30", "count": 25}
  ]
}
```

**Metrics Explained:**
- `total` - Total attendance records today
- `late` - Clock-in at or after 10:00 AM
- `overtime` - Clock-out at or after 6:00 PM
- `ontime` - Clock-in before 10:00 AM
- `absent` - Registered persons who haven't clocked in today

---

## Settings Management

### 8. Get Settings
Retrieve current office location and geofence settings.

**Endpoint:** `GET /api/settings`

**Response:**
```json
{
  "latitude": 23.022797,
  "longitude": 72.531968,
  "radius": 10000
}
```

---

### 9. Update Settings
Update office location and geofence radius.

**Endpoint:** `POST /api/settings`

**Request Body:**
```json
{
  "latitude": 23.022797,
  "longitude": 72.531968,
  "radius": 50
}
```

**Response:**
```json
{
  "success": true,
  "settings": {
    "latitude": 23.022797,
    "longitude": 72.531968,
    "radius": 50
  }
}
```

---

### 10. Get Allowed IPs
Retrieve list of whitelisted IP addresses.

**Endpoint:** `GET /api/allowed-ips`

**Response:**
```json
{
  "success": true,
  "ips": [
    {
      "id": 1,
      "ip_address": "127.0.0.1",
      "description": "Localhost",
      "is_active": true,
      "created_at": "2024-01-15T10:00:00+05:30"
    },
    {
      "id": 2,
      "ip_address": "192.168.1.100",
      "description": "Office Network",
      "is_active": true,
      "created_at": "2024-01-15T10:05:00+05:30"
    }
  ]
}
```

---

### 11. Add Allowed IP
Add a new IP address to the whitelist.

**Endpoint:** `POST /api/allowed-ips`

**Request Body:**
```json
{
  "ip_address": "192.168.1.100",
  "description": "Office Network"
}
```

**Response:**
```json
{
  "success": true,
  "ip": {
    "id": 2,
    "ip_address": "192.168.1.100",
    "description": "Office Network",
    "is_active": true,
    "created_at": "2024-01-15T10:05:00+05:30"
  }
}
```

---

### 12. Delete Allowed IP
Remove an IP address from the whitelist.

**Endpoint:** `DELETE /api/allowed-ips/{ip_id}`

**Response:**
```json
{
  "success": true
}
```

---

### 13. Toggle IP Status
Enable or disable an IP address without deleting it.

**Endpoint:** `POST /api/allowed-ips/{ip_id}/toggle`

**Response:**
```json
{
  "success": true,
  "ip": {
    "id": 2,
    "ip_address": "192.168.1.100",
    "description": "Office Network",
    "is_active": false,
    "created_at": "2024-01-15T10:05:00+05:30"
  }
}
```

---

## Error Handling

All API endpoints follow a consistent error response format:

```json
{
  "success": false,
  "error": "Error message description"
}
```

### Common HTTP Status Codes
- `200` - Success
- `400` - Bad Request (missing or invalid parameters)
- `403` - Forbidden (IP or location validation failed)
- `404` - Not Found (resource doesn't exist)
- `422` - Unprocessable Entity (face detection issues)
- `500` - Internal Server Error

---

## Integration Examples

### JavaScript (Fetch API)

```javascript
// Register Person
async function registerPerson(name, empCode, imageBase64) {
  const response = await fetch('http://127.0.0.1:5000/api/register-face-live', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: name,
      employee_code: empCode,
      image: imageBase64
    })
  });
  return await response.json();
}

// Clock In
async function clockIn(imageBase64, lat, lng) {
  const response = await fetch('http://127.0.0.1:5000/api/attendance/clock', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      image: imageBase64,
      action: 'clock_in',
      latitude: lat,
      longitude: lng
    })
  });
  return await response.json();
}

// Get Analytics
async function getAnalytics() {
  const response = await fetch('http://127.0.0.1:5000/api/analytics/dashboard');
  return await response.json();
}
```

---

### Python (Requests)

```python
import requests
import base64

BASE_URL = "http://127.0.0.1:5000"

# Register Person
def register_person(name, emp_code, image_path):
    with open(image_path, 'rb') as f:
        image_base64 = f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}"
    
    response = requests.post(
        f"{BASE_URL}/api/register-face-live",
        json={
            "name": name,
            "employee_code": emp_code,
            "image": image_base64
        }
    )
    return response.json()

# Clock In
def clock_in(image_base64, lat, lng):
    response = requests.post(
        f"{BASE_URL}/api/attendance/clock",
        json={
            "image": image_base64,
            "action": "clock_in",
            "latitude": lat,
            "longitude": lng
        }
    )
    return response.json()

# Get Analytics
def get_analytics():
    response = requests.get(f"{BASE_URL}/api/analytics/dashboard")
    return response.json()
```

---

### cURL

```bash
# Register Person
curl -X POST http://127.0.0.1:5000/api/register-face-live \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "employee_code": "EMP001",
    "image": "data:image/jpeg;base64,/9j/4AAQ..."
  }'

# Clock In
curl -X POST http://127.0.0.1:5000/api/attendance/clock \
  -H "Content-Type: application/json" \
  -d '{
    "image": "data:image/jpeg;base64,/9j/4AAQ...",
    "action": "clock_in",
    "latitude": 23.022797,
    "longitude": 72.531968
  }'

# Get Analytics
curl http://127.0.0.1:5000/api/analytics/dashboard
```

---

## Security Considerations

1. **IP Whitelist**: Configure allowed IPs in `/api/allowed-ips`
2. **Geofencing**: Set appropriate radius (recommended: 50m for production)
3. **HTTPS**: Use HTTPS in production environments
4. **Rate Limiting**: Implement rate limiting for production
5. **CORS**: Configure CORS settings for cross-origin requests

---

## Timezone

All timestamps are in **Indian Standard Time (IST - Asia/Kolkata, UTC+5:30)**

---

## Support

For issues or questions:
- Check the main README.md
- Review error messages in API responses
- Ensure IP is whitelisted
- Verify location permissions are granted

---

## Version

API Version: 1.0  
Last Updated: January 2024
