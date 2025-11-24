# How to Enable Location Access

## Error: "Location unavailable. Please check your device settings"

This means your device's location services are turned off. Follow these steps:

---

## 🖥️ Windows PC/Laptop

### Step 1: Enable Windows Location
1. Press `Windows + I` (or click Start → Settings)
2. Click **Privacy & Security**
3. Click **Location** in the left sidebar
4. Toggle ON **Location services**
5. Toggle ON **Let apps access your location**

### Step 2: Enable Browser Location
**For Chrome:**
1. Click the lock icon 🔒 in the address bar
2. Click **Site settings**
3. Find **Location** → Select **Allow**
4. Refresh the page (F5)

**For Edge:**
1. Click the lock icon 🔒 in the address bar
2. Click **Permissions for this site**
3. Set **Location** to **Allow**
4. Refresh the page (F5)

**For Firefox:**
1. Click the lock icon 🔒 in the address bar
2. Click arrow next to **Connection secure**
3. Click **More information**
4. Go to **Permissions** tab
5. Find Location → Uncheck "Use Default"
6. Check **Allow**
7. Refresh the page (F5)

---

## 📱 Android Phone/Tablet

1. Open **Settings**
2. Tap **Location** (or **Security & Location**)
3. Toggle ON **Use location**
4. Open your browser
5. Go to browser Settings → Site settings → Location
6. Allow location for `127.0.0.1` or your site

---

## 📱 iPhone/iPad

1. Open **Settings**
2. Tap **Privacy**
3. Tap **Location Services**
4. Toggle ON **Location Services**
5. Scroll down to **Safari** (or your browser)
6. Select **While Using the App**

---

## 🔧 Still Not Working?

### Check if location is working:
1. Open a new tab
2. Go to: https://www.google.com/maps
3. Click the "My Location" button (blue dot)
4. If it shows your location → Location is working
5. If not → Your device doesn't have GPS or it's disabled

### For Desktop/Laptop without GPS:
- Most desktops don't have GPS
- Location will be approximate (based on IP address)
- This is normal and should still work for testing

### Quick Test:
1. Open browser console (F12)
2. Go to Console tab
3. Type: `navigator.geolocation.getCurrentPosition(pos => console.log(pos))`
4. Press Enter
5. If you see coordinates → Location is working
6. If you see error → Location is blocked

---

## ✅ After Enabling Location

1. Go back to the Clock In/Out page
2. Refresh the page (F5)
3. Click "Allow" when browser asks for location
4. You should see: ✅ Location: [coordinates]
5. Now you can Clock In/Out

---

## 🎯 Current Configuration

Your office location is set to:
- **Latitude:** 21.189603818522603
- **Longitude:** 72.78278586697415
- **Location:** Surat, Gujarat, India
- **Geofence Radius:** 10,000 meters (10 km) - FOR TESTING

This large radius means you can test from anywhere within 10km of the office location.

For production, change `GEOFENCE_RADIUS_METERS` in `config.py` to `50` (50 meters).
