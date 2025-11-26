# API Quick Reference Guide

## Base URL
```
http://127.0.0.1:5000
```

---

## 🚀 Quick Start Endpoints

### 1. Register Person
```http
POST /api/register-face-live
Content-Type: application/json

{
  "name": "John Doe",
  "employee_code": "EMP001",
  "image": "data:image/jpeg;base64,..."
}
```

### 2. Clock In
```http
POST /api/attendance/clock
Content-Type: application/json

{
  "image": "data:image/jpeg;base64,...",
  "action": "clock_in",
  "latitude": 23.022797,
  "longitude": 72.531968
}
```

### 3. Clock Out
```http
POST /api/attendance/clock
Content-Type: application/json

{
  "image": "data:image/jpeg;base64,...",
  "action": "clock_out",
  "latitude": 23.022797,
  "longitude": 72.531968
}
```

### 4. Get Analytics
```http
GET /api/analytics/dashboard
```

### 5. Get Latest Attendance
```http
GET /api/attendance/latest
```

### 6. Break In
```http
POST /api/attendance/break
Content-Type: application/json

{
  "action": "break_in",
  "latitude": 23.022797,
  "longitude": 72.531968
}
```

### 7. Break Out
```http
POST /api/attendance/break
Content-Type: application/json

{
  "action": "break_out",
  "latitude": 23.022797,
  "longitude": 72.531968
}
```

### 8. Add Holiday
```http
POST /api/holidays
Content-Type: application/json

{
  "date": "2024-01-26",
  "name": "Republic Day",
  "is_weekoff": false
}
```

### 9. Get Holidays
```http
GET /api/holidays?year=2024&month=1
```

---

## 📊 All Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/register-face-live` | Register person with base64 image |
| `POST` | `/api/register-face` | Register person with file upload |
| `DELETE` | `/api/persons/{id}` | Delete person |
| `POST` | `/api/attendance/clock` | Clock in/out with validation |
| `POST` | `/api/attendance/break` | Break in/out |
| `POST` | `/api/attendance/live-mark` | Mark attendance (legacy) |
| `GET` | `/api/attendance/latest` | Get 20 recent records |
| `GET` | `/api/analytics/dashboard` | Get analytics data |
| `GET` | `/api/holidays` | Get holidays for month |
| `POST` | `/api/holidays` | Add new holiday |
| `DELETE` | `/api/holidays/{id}` | Delete holiday |
| `GET` | `/api/settings` | Get office settings |
| `POST` | `/api/settings` | Update office settings |
| `GET` | `/api/allowed-ips` | Get IP whitelist |
| `POST` | `/api/allowed-ips` | Add IP to whitelist |
| `DELETE` | `/api/allowed-ips/{id}` | Remove IP from whitelist |
| `POST` | `/api/allowed-ips/{id}/toggle` | Enable/disable IP |

---

## 🔑 Response Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `400` | Bad Request |
| `403` | Forbidden (IP/Location) |
| `404` | Not Found |
| `422` | Face Detection Error |
| `500` | Server Error |

---

## 💡 Common Use Cases

### Use Case 1: Employee Registration Flow
```javascript
// 1. Capture image from camera
const imageBase64 = canvas.toDataURL('image/jpeg');

// 2. Register employee
const result = await fetch('/api/register-face-live', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    name: 'John Doe',
    employee_code: 'EMP001',
    image: imageBase64
  })
});
```

### Use Case 2: Daily Attendance Flow
```javascript
// 1. Get user location
navigator.geolocation.getCurrentPosition(async (pos) => {
  // 2. Capture face image
  const imageBase64 = canvas.toDataURL('image/jpeg');
  
  // 3. Clock in
  const result = await fetch('/api/attendance/clock', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      image: imageBase64,
      action: 'clock_in',
      latitude: pos.coords.latitude,
      longitude: pos.coords.longitude
    })
  });
});
```

### Use Case 3: Break Management
```javascript
// Break In
navigator.geolocation.getCurrentPosition(async (pos) => {
  const result = await fetch('/api/attendance/break', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      action: 'break_in',
      latitude: pos.coords.latitude,
      longitude: pos.coords.longitude
    })
  });
});

// Break Out (after 30 minutes)
navigator.geolocation.getCurrentPosition(async (pos) => {
  const result = await fetch('/api/attendance/break', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      action: 'break_out',
      latitude: pos.coords.latitude,
      longitude: pos.coords.longitude
    })
  });
});
```

### Use Case 4: Holiday Management
```javascript
// Add holiday
await fetch('/api/holidays', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    date: '2024-01-26',
    name: 'Republic Day',
    is_weekoff: false
  })
});

// Get holidays for current month
const holidays = await fetch('/api/holidays')
  .then(res => res.json());

console.log(holidays.holidays);
```

### Use Case 5: Dashboard Integration
```javascript
// Fetch analytics for dashboard
const analytics = await fetch('/api/analytics/dashboard')
  .then(res => res.json());

console.log(`Present: ${analytics.today.total}`);
console.log(`Absent: ${analytics.today.absent}`);
console.log(`Late: ${analytics.today.late}`);
```

---

## ⚙️ Configuration

### Set Office Location
```javascript
await fetch('/api/settings', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    latitude: 23.022797,
    longitude: 72.531968,
    radius: 50  // meters
  })
});
```

### Add Allowed IP
```javascript
await fetch('/api/allowed-ips', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    ip_address: '192.168.1.100',
    description: 'Office Network'
  })
});
```

---

## 🛡️ Security Checklist

- [ ] Configure IP whitelist
- [ ] Set appropriate geofence radius (50m recommended)
- [ ] Use HTTPS in production
- [ ] Implement rate limiting
- [ ] Configure CORS properly
- [ ] Validate all inputs
- [ ] Monitor failed attempts

---

## 📱 Mobile App Integration

### React Native Example
```javascript
import * as Location from 'expo-location';
import { Camera } from 'expo-camera';

const clockIn = async () => {
  // Get location
  const location = await Location.getCurrentPositionAsync({});
  
  // Capture photo
  const photo = await camera.takePictureAsync({base64: true});
  const imageBase64 = `data:image/jpeg;base64,${photo.base64}`;
  
  // Clock in
  const response = await fetch('http://YOUR_SERVER:5000/api/attendance/clock', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      image: imageBase64,
      action: 'clock_in',
      latitude: location.coords.latitude,
      longitude: location.coords.longitude
    })
  });
  
  return await response.json();
};
```

---

## 🌐 Web Integration

### HTML + JavaScript
```html
<!DOCTYPE html>
<html>
<head>
  <title>Attendance System</title>
</head>
<body>
  <video id="video" autoplay></video>
  <button onclick="clockIn()">Clock In</button>
  
  <script>
    const video = document.getElementById('video');
    
    // Start camera
    navigator.mediaDevices.getUserMedia({video: true})
      .then(stream => video.srcObject = stream);
    
    async function clockIn() {
      // Get location
      navigator.geolocation.getCurrentPosition(async (pos) => {
        // Capture frame
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0);
        const imageBase64 = canvas.toDataURL('image/jpeg');
        
        // Clock in
        const response = await fetch('http://127.0.0.1:5000/api/attendance/clock', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            image: imageBase64,
            action: 'clock_in',
            latitude: pos.coords.latitude,
            longitude: pos.coords.longitude
          })
        });
        
        const result = await response.json();
        alert(result.success ? result.message : result.error);
      });
    }
  </script>
</body>
</html>
```

---

## 🐍 Python Integration

```python
import requests
import base64
from datetime import datetime

class AttendanceAPI:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
    
    def register_person(self, name, emp_code, image_path):
        with open(image_path, 'rb') as f:
            image_b64 = base64.b64encode(f.read()).decode()
        
        return requests.post(
            f"{self.base_url}/api/register-face-live",
            json={
                "name": name,
                "employee_code": emp_code,
                "image": f"data:image/jpeg;base64,{image_b64}"
            }
        ).json()
    
    def clock_in(self, image_path, lat, lng):
        with open(image_path, 'rb') as f:
            image_b64 = base64.b64encode(f.read()).decode()
        
        return requests.post(
            f"{self.base_url}/api/attendance/clock",
            json={
                "image": f"data:image/jpeg;base64,{image_b64}",
                "action": "clock_in",
                "latitude": lat,
                "longitude": lng
            }
        ).json()
    
    def get_analytics(self):
        return requests.get(
            f"{self.base_url}/api/analytics/dashboard"
        ).json()
    
    def break_in(self, lat, lng):
        return requests.post(
            f"{self.base_url}/api/attendance/break",
            json={
                "action": "break_in",
                "latitude": lat,
                "longitude": lng
            }
        ).json()
    
    def break_out(self, lat, lng):
        return requests.post(
            f"{self.base_url}/api/attendance/break",
            json={
                "action": "break_out",
                "latitude": lat,
                "longitude": lng
            }
        ).json()
    
    def add_holiday(self, date, name, is_weekoff=False):
        return requests.post(
            f"{self.base_url}/api/holidays",
            json={
                "date": date,
                "name": name,
                "is_weekoff": is_weekoff
            }
        ).json()
    
    def get_holidays(self, year=None, month=None):
        params = {}
        if year:
            params['year'] = year
        if month:
            params['month'] = month
        return requests.get(
            f"{self.base_url}/api/holidays",
            params=params
        ).json()

# Usage
api = AttendanceAPI()
result = api.register_person("John Doe", "EMP001", "photo.jpg")
print(result)

# Break management
api.break_in(23.022797, 72.531968)
api.break_out(23.022797, 72.531968)

# Holiday management
api.add_holiday("2024-01-26", "Republic Day", False)
holidays = api.get_holidays(2024, 1)
print(holidays)
```

---

## 📞 Support

For detailed documentation, see `API_DOCUMENTATION.md`

**Common Issues:**
- **403 Error**: Check IP whitelist and location
- **422 Error**: Ensure clear face image
- **400 Error**: Verify all required fields

---

## 📝 Notes

- All timestamps in IST (UTC+5:30)
- Image format: Base64 encoded JPEG/PNG
- Geofence radius in meters
- Late threshold: 10:00 AM
- Overtime threshold: 6:00 PM
- Duplicate prevention: 1 minute window
