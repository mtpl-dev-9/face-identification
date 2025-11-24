# Settings Management Guide

## ✅ What Changed

Office location and geofence radius are now stored in the **database** instead of code!

You can now change these settings from the web interface without editing `config.py`.

---

## 🎯 How to Use

### 1. Access Settings Page
- Open your application: http://127.0.0.1:5000
- Click **⚙️ Settings** in the navigation menu

### 2. Update Office Location
**Option A: Enter Manually**
- Get coordinates from Google Maps
- Enter Latitude and Longitude
- Click "Save Settings"

**Option B: Use Current Location**
- Click "📍 Use My Current Location" button
- Allow location access
- Click "Save Settings"

**Option C: Use Helper Page**
- Click "🗺️ Get Location Helper"
- Follow instructions to get coordinates
- Copy and paste into settings

### 3. Update Geofence Radius
- Enter radius in meters
- Recommended values:
  - **Testing:** 10000 (10 km)
  - **Production:** 50-100 meters
  - **Strict:** 20-30 meters
- Click "Save Settings"

---

## 📊 Current Default Settings

From `config.py` (used if database is empty):
- **Latitude:** 23.022797
- **Longitude:** 72.531968
- **Location:** Ahmedabad, Gujarat, India
- **Radius:** 10000 meters (10 km)

---

## 🔄 How It Works

1. **First Time:**
   - System uses values from `config.py`
   - No database entries yet

2. **After Saving Settings:**
   - Values are stored in database
   - System uses database values
   - `config.py` values become fallback only

3. **Priority:**
   - Database settings (if exist) ✅
   - Config.py settings (fallback) ⬇️

---

## 🛠️ API Endpoints

### Get Settings
```bash
GET /api/settings
```

Response:
```json
{
  "latitude": 23.022797,
  "longitude": 72.531968,
  "radius": 10000
}
```

### Update Settings
```bash
POST /api/settings
Content-Type: application/json

{
  "latitude": 23.022797,
  "longitude": 72.531968,
  "radius": 50
}
```

Response:
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

## 💡 Benefits

✅ **No Code Changes:** Update settings from web interface
✅ **Instant Updates:** Changes apply immediately
✅ **Easy Management:** Non-technical users can update
✅ **Audit Trail:** Database tracks when settings changed
✅ **Backup Friendly:** Settings stored in database backups
✅ **Multi-Environment:** Different settings per deployment

---

## 🔐 Security Note

The settings page is currently accessible to anyone. For production:

1. Add authentication/authorization
2. Restrict access to admin users only
3. Log all settings changes
4. Add confirmation before saving

---

## 📝 Database Table

Settings are stored in the `settings` table:

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| key | VARCHAR(50) | Setting name (unique) |
| value | VARCHAR(200) | Setting value |
| updated_at | DATETIME | Last update time |

Current keys:
- `office_latitude`
- `office_longitude`
- `geofence_radius`

---

## 🚀 Quick Start

1. Run migration (if not done):
   ```bash
   python migrate_db.py
   ```

2. Start application:
   ```bash
   python app.py
   ```

3. Go to Settings:
   ```
   http://127.0.0.1:5000/settings
   ```

4. Update your office location and radius

5. Click "Save Settings"

6. Test clock in/out with new settings!

---

## ❓ Troubleshooting

**Settings not saving?**
- Check database file exists: `instance/attendance.db`
- Run migration: `python migrate_db.py`
- Check browser console for errors

**Settings not applying?**
- Refresh the page
- Check `/api/settings` endpoint
- Verify database has entries

**Want to reset to defaults?**
- Delete entries from settings table
- Or update via settings page
