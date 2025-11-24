# Timezone Configuration

## ✅ Indian Standard Time (IST) Configured

The system now uses **Indian Standard Time (IST)** for all timestamps.

### Timezone Details:
- **Timezone:** Asia/Kolkata (IST)
- **UTC Offset:** +05:30
- **Time Format:** 24-hour format

### What Changed:

1. **All timestamps now show IST time:**
   - Clock in/out times
   - Attendance records
   - Person registration times
   - Settings update times

2. **Database records:**
   - All new records use IST
   - Existing records remain unchanged (were in UTC)

3. **Display format:**
   - Times shown in reports: IST
   - Clock in/out messages: IST
   - Attendance logs: IST

### Example:
- **Before:** 2024-01-15 04:30:00 (UTC)
- **After:** 2024-01-15 10:00:00 (IST)

### Technical Implementation:
```python
import pytz
IST = pytz.timezone('Asia/Kolkata')

# Get current IST time
now = datetime.now(IST)
```

### Verification:
To verify the timezone is working:
1. Clock in/out
2. Check the time displayed
3. It should match your local Indian time

### Note:
- Old records in database may still show UTC time
- New records from now on will use IST
- The system automatically handles timezone conversion
