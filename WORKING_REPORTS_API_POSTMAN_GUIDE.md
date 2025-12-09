# Working Reports API - Postman Testing Guide

## Base URL
```
http://127.0.0.1:5000
```

## API Endpoint
```
GET /api/working-reports
```

---

## Test Scenarios

### 1. Only User ID (Last 7 Days)
**Request Type:** GET  
**URL:** `http://127.0.0.1:5000/api/working-reports?user_id=1`

**Query Parameters:**
- `user_id`: 1 (required)

**Expected Response:**
```json
{
  "success": true,
  "records": [
    {
      "user_full_name": "Jay Chauhan",
      "date": "2025-12-05",
      "clock_in_time": "09:00:00",
      "clock_out_time": "18:00:00",
      "worked_hours": 8.5,
      "total_hours_difference": 0.5,
      "note": null
    }
  ],
  "search_info": {
    "user_id": 1,
    "date_range": "2025-11-28 to 2025-12-05",
    "attendance_records_found": 5,
    "manual_entries_found": 2,
    "existing_records_found": 3
  }
}
```

---

### 2. User ID + Date (Specific Day)
**Request Type:** GET  
**URL:** `http://127.0.0.1:5000/api/working-reports?user_id=1&date=28`

**Query Parameters:**
- `user_id`: 1 (required)
- `date`: 28 (day number, 1-31)

**Note:** Uses current month/year if month/year not provided

**Expected Response:**
```json
{
  "success": true,
  "records": [
    {
      "user_full_name": "Jay Chauhan",
      "date": "2025-12-28",
      "clock_in_time": "09:00:00",
      "clock_out_time": "18:00:00",
      "worked_hours": 8.0,
      "total_hours_difference": 0.0,
      "note": null
    }
  ],
  "search_info": {
    "user_id": 1,
    "date_range": "2025-12-28 to 2025-12-28",
    "attendance_records_found": 1,
    "manual_entries_found": 0,
    "existing_records_found": 0
  }
}
```

---

### 3. User ID + Date + Month + Year (Specific Date)
**Request Type:** GET  
**URL:** `http://127.0.0.1:5000/api/working-reports?user_id=1&date=28&month=11&year=2025`

**Query Parameters:**
- `user_id`: 1 (required)
- `date`: 28 (day number)
- `month`: 11
- `year`: 2025

**Expected Response:**
```json
{
  "success": true,
  "records": [
    {
      "user_full_name": "Jay Chauhan",
      "date": "2025-11-28",
      "clock_in_time": "09:00:00",
      "clock_out_time": "18:00:00",
      "worked_hours": 8.5,
      "total_hours_difference": 0.5,
      "note": null
    }
  ],
  "search_info": {
    "user_id": 1,
    "date_range": "2025-11-28 to 2025-11-28",
    "attendance_records_found": 1,
    "manual_entries_found": 0,
    "existing_records_found": 0
  }
}
```

---

### 4. User ID + Month (Entire Month in Current Year)
**Request Type:** GET  
**URL:** `http://127.0.0.1:5000/api/working-reports?user_id=1&month=11`

**Query Parameters:**
- `user_id`: 1 (required)
- `month`: 11 (1-12)

**Expected Response:**
```json
{
  "success": true,
  "records": [
    {
      "user_full_name": "Jay Chauhan",
      "date": "2025-11-01",
      "clock_in_time": "09:00:00",
      "clock_out_time": "18:00:00",
      "worked_hours": 8.0,
      "total_hours_difference": 0.0,
      "note": null
    },
    {
      "user_full_name": "Jay Chauhan",
      "date": "2025-11-02",
      "clock_in_time": "09:00:00",
      "clock_out_time": "18:00:00",
      "worked_hours": 8.0,
      "total_hours_difference": 0.0,
      "note": null
    }
    // ... more records for the month
  ],
  "search_info": {
    "user_id": 1,
    "date_range": "2025-11-01 to 2025-11-30",
    "attendance_records_found": 20,
    "manual_entries_found": 5,
    "existing_records_found": 15
  }
}
```

---

### 5. User ID + Year + Month (Specific Month in Specific Year)
**Request Type:** GET  
**URL:** `http://127.0.0.1:5000/api/working-reports?user_id=1&year=2025&month=11`

**Query Parameters:**
- `user_id`: 1 (required)
- `year`: 2025
- `month`: 11 (required when year is provided)

**Expected Response:**
```json
{
  "success": true,
  "records": [
    // All records for November 2025
  ],
  "search_info": {
    "user_id": 1,
    "date_range": "2025-11-01 to 2025-11-30",
    "attendance_records_found": 20,
    "manual_entries_found": 5,
    "existing_records_found": 15
  }
}
```

---

## Error Responses

### Missing User ID
**URL:** `http://127.0.0.1:5000/api/working-reports`

**Response:**
```json
{
  "success": false,
  "error": "user_id is required"
}
```
**Status Code:** 400

---

### User Not Found
**URL:** `http://127.0.0.1:5000/api/working-reports?user_id=999`

**Response:**
```json
{
  "success": false,
  "error": "User not found or inactive"
}
```
**Status Code:** 404

---

### Invalid Date
**URL:** `http://127.0.0.1:5000/api/working-reports?user_id=1&date=32`

**Response:**
```json
{
  "success": false,
  "error": "Invalid date: Day 32 doesn't exist in month 12/2025"
}
```
**Status Code:** 400

---

## Postman Setup Instructions

### Step 1: Create a New Request
1. Open Postman
2. Click "New" → "HTTP Request"
3. Set method to **GET**

### Step 2: Enter URL
```
http://127.0.0.1:5000/api/working-reports
```

### Step 3: Add Query Parameters
Go to the **Params** tab and add:

| Key | Value | Description |
|-----|-------|-------------|
| user_id | 1 | Required - User ID |
| date | 28 | Optional - Day number (1-31) |
| month | 11 | Optional - Month (1-12) |
| year | 2025 | Optional - Year |

### Step 4: Send Request
Click **Send** button

### Step 5: View Response
Check the response body for JSON data with:
- `success`: true/false
- `records`: Array of working records
- `search_info`: Debug information about the search

---

## Testing Checklist

- [ ] Test with only user_id (should return last 7 days)
- [ ] Test with user_id + date (should return specific day)
- [ ] Test with user_id + month (should return entire month)
- [ ] Test with user_id + year + month (should return specific month)
- [ ] Test with invalid user_id (should return 404 error)
- [ ] Test without user_id (should return 400 error)
- [ ] Test with invalid date (e.g., date=32, should return 400 error)
- [ ] Verify response includes all required fields
- [ ] Verify worked_hours calculation is correct
- [ ] Verify total_hours_difference shows positive/negative correctly

---

## Example Postman Collection JSON

You can import this into Postman:

```json
{
  "info": {
    "name": "Working Reports API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Get Last 7 Days",
      "request": {
        "method": "GET",
        "url": {
          "raw": "http://127.0.0.1:5000/api/working-reports?user_id=1",
          "query": [
            {"key": "user_id", "value": "1"}
          ]
        }
      }
    },
    {
      "name": "Get Specific Day",
      "request": {
        "method": "GET",
        "url": {
          "raw": "http://127.0.0.1:5000/api/working-reports?user_id=1&date=28&month=11&year=2025",
          "query": [
            {"key": "user_id", "value": "1"},
            {"key": "date", "value": "28"},
            {"key": "month", "value": "11"},
            {"key": "year", "value": "2025"}
          ]
        }
      }
    },
    {
      "name": "Get Entire Month",
      "request": {
        "method": "GET",
        "url": {
          "raw": "http://127.0.0.1:5000/api/working-reports?user_id=1&month=11&year=2025",
          "query": [
            {"key": "user_id", "value": "1"},
            {"key": "month", "value": "11"},
            {"key": "year", "value": "2025"}
          ]
        }
      }
    }
  ]
}
```

---

## Tips

1. **Start with a valid user_id** - Check your `mtpl_users` table to get a valid user ID
2. **Check date ranges** - Make sure the dates you're searching have data
3. **Use search_info** - The `search_info` field shows how many records were found from each source
4. **Test incrementally** - Start with just user_id, then add filters one by one
5. **Check Swagger UI** - Visit `http://127.0.0.1:5000/api/docs#/` for interactive API testing

---

## Common Issues

### Issue: "No records found"
**Solution:** 
- Verify the user_id exists in `mtpl_users` table
- Check if there's data in `mtpl_attendance` or `mtpl_manual_time_entries` for that user
- Verify the date range is correct
- Try searching with only user_id first (last 7 days)

### Issue: "User not found or inactive"
**Solution:**
- Check if user exists: `SELECT * FROM mtpl_users WHERE userId = 1`
- Verify user is active: `userIsActive = '1'`

### Issue: "Invalid date"
**Solution:**
- Date must be between 1-31
- Month must be between 1-12
- Year must be reasonable (2000-2100)
- Check if the day exists in that month (e.g., Feb 30 doesn't exist)

