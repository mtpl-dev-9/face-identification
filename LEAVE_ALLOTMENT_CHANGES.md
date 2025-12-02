# Leave Allotment System - Changes Summary

## Overview

The Leave Allotment System has been updated to use the `mtpl_leave_allotment` table for storing leave allocations. This table is now the primary source for displaying leave balances to employees.

## What Changed?

### 1. Database Table: `mtpl_leave_allotment`

**Purpose:** Store leave allocations for employees

**Columns:**
- `allotmentId` - Primary key
- `allotmentUserId` - User ID (references mtpl_users)
- `allotmentLeaveTypeId` - Leave type ID (references mtpl_leave_types)
- `allotmentTotal` - Total leaves allocated (DECIMAL supports 0.5, 12.5, etc.)
- `allotmentYear` - Year for allocation
- `allotmentAssignedBy` - Who assigned the leaves
- `allotmentAssignedAt` - When assigned
- `allotmentUpdatedAt` - Last update timestamp

**Example Data:**
```sql
-- User 1 has 4 Casual, 7 Sick, 0.5 Celebratory leaves for 2024
allotmentId | allotmentUserId | allotmentLeaveTypeId | allotmentTotal | allotmentYear
1           | 1               | 1                    | 4.0            | 2024
2           | 1               | 2                    | 7.0            | 2024
3           | 1               | 3                    | 0.5            | 2024
```

### 2. New API Endpoints

#### Get Leave Allotments
```http
GET /api/leave-allotments?user_id={id}&year={year}
```

#### Create Leave Allotment
```http
POST /api/leave-allotments
Body: {
  "user_id": 1,
  "leave_type_id": 1,
  "total": 4,
  "year": 2024,
  "assigned_by": 1
}
```

#### Bulk Assign Leaves
```http
POST /api/leave-allotments/bulk
Body: {
  "user_ids": [1, 2, 3],
  "leave_type_id": 1,
  "total": 4,
  "year": 2024,
  "assigned_by": 1
}
```

#### Assign Default Leaves to All Users
```http
POST /api/leave-allotments/default
Body: {
  "year": 2024,
  "defaults": {
    "casual": 4,
    "sick": 7,
    "celebratory": 0.5
  },
  "assigned_by": 1
}
```

#### Delete Leave Allotment
```http
DELETE /api/leave-allotments/{id}
```

### 3. Updated Frontend (leave_management.html)

**Changed Functions:**
- `assignLeaveBalance()` - Now uses `/api/leave-allotments`
- `loadEmployeeBalance()` - Now fetches from `/api/leave-allotments`
- `bulkAssignLeaveBalance()` - Now uses `/api/leave-allotments/bulk`
- `assignDefaultLeaves()` - Now uses `/api/leave-allotments/default`

**Display Format:**
```
Casual Leave
Total: 4 | Used: 0 | Remaining: 4

Sick Leave
Total: 7 | Used: 0 | Remaining: 7

Celebratory Leave
Total: 0.5 | Used: 0 | Remaining: 0.5
```

### 4. New Files Created

1. **leave_allotment_schema.sql**
   - SQL schema for creating the table
   - Run: `mysql -u admin -p mtpl_website < leave_allotment_schema.sql`

2. **init_leave_allotment.py**
   - Python script to initialize the system
   - Run: `python init_leave_allotment.py`

3. **LEAVE_ALLOTMENT_GUIDE.md**
   - Complete documentation for the system
   - Includes API reference, database queries, examples

4. **test_leave_allotment.py**
   - Test script to verify everything works
   - Run: `python test_leave_allotment.py`

5. **LEAVE_ALLOTMENT_CHANGES.md**
   - This file - summary of all changes

### 5. Updated Files

1. **app.py**
   - Added `/api/leave-allotments/*` endpoints
   - Added `LeaveType` import
   - Added `api_assign_default_leave_allotments()` function

2. **models.py**
   - Already had `LeaveAllotment` model (no changes needed)

3. **templates/leave_management.html**
   - Updated JavaScript functions to use new endpoints
   - Changed API calls from `/api/user-leave-balance` to `/api/leave-allotments`

4. **README.md**
   - Updated documentation
   - Added new API endpoints
   - Updated database structure section

## How It Works

### Workflow

1. **Admin assigns leaves:**
   ```
   Admin → Assign Leave Balance → mtpl_leave_allotment table
   ```

2. **Employee views balance:**
   ```
   Employee Panel → Fetch from mtpl_leave_allotment → Display
   ```

3. **Data stored in database:**
   ```sql
   SELECT * FROM mtpl_leave_allotment WHERE allotmentUserId = 1 AND allotmentYear = 2024;
   ```

### Example Usage

**Scenario: Assign 4 Casual Leaves to User 1**

1. **Via Web Interface:**
   - Go to http://127.0.0.1:5000/leave-management
   - Select User 1
   - Select "Casual Leave"
   - Enter 4
   - Click "Assign Balance"

2. **Via API:**
   ```bash
   curl -X POST http://127.0.0.1:5000/api/leave-allotments \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": 1,
       "leave_type_id": 1,
       "total": 4,
       "year": 2024,
       "assigned_by": 1
     }'
   ```

3. **Verify in Database:**
   ```sql
   SELECT 
     u.userFirstName,
     u.userLastName,
     lt.leaveTypeName,
     a.allotmentTotal,
     a.allotmentYear
   FROM mtpl_leave_allotment a
   JOIN mtpl_users u ON a.allotmentUserId = u.userId
   JOIN mtpl_leave_types lt ON a.allotmentLeaveTypeId = lt.leaveTypeId
   WHERE a.allotmentUserId = 1;
   ```

## Benefits

1. **Persistent Storage:** All leave allocations stored in database
2. **Audit Trail:** Tracks who assigned leaves and when
3. **Decimal Support:** Can assign 0.5, 12.5, etc.
4. **Bulk Operations:** Assign to multiple users at once
5. **Year-wise Tracking:** Separate allocations per year
6. **Easy Queries:** Simple SQL queries to view data

## Migration from Old System

If you were using `mtpl_user_leave_balance` before:

1. **Both tables can coexist:**
   - `mtpl_leave_allotment` - For allocations (what's assigned)
   - `mtpl_user_leave_balance` - For tracking usage (what's used)

2. **No data loss:**
   - Old data remains in `mtpl_user_leave_balance`
   - New allocations go to `mtpl_leave_allotment`

3. **Gradual migration:**
   - Start using new system for new allocations
   - Keep old data for historical reference

## Testing

### Quick Test

```bash
# 1. Initialize system
python init_leave_allotment.py

# 2. Run test
python test_leave_allotment.py

# 3. Start app
python app.py

# 4. Open browser
http://127.0.0.1:5000/leave-management

# 5. Assign default leaves
Click "Assign Default Leaves" → "Assign to All Users"

# 6. Check database
mysql -u admin -p mtpl_website
SELECT * FROM mtpl_leave_allotment;
```

### Expected Result

After assigning default leaves, you should see:
- 3 records per user (Casual, Sick, Celebratory)
- Total records = Number of users × 3
- Data visible in Employee Panel

## Troubleshooting

### Issue: Table doesn't exist

**Solution:**
```bash
mysql -u admin -p mtpl_website < leave_allotment_schema.sql
```

### Issue: No data showing

**Solution:**
1. Check if table has data: `SELECT COUNT(*) FROM mtpl_leave_allotment;`
2. If empty, use "Assign Default Leaves" in web interface
3. Or run: `python init_leave_allotment.py`

### Issue: API returns empty array

**Solution:**
1. Verify user_id exists: `SELECT * FROM mtpl_users WHERE userId = 1;`
2. Verify year is correct: Use current year (2024)
3. Check if allotments exist for that user/year

## Support

For questions or issues:
- Read: `LEAVE_ALLOTMENT_GUIDE.md`
- Check: `leave_allotment_schema.sql`
- Test: `python test_leave_allotment.py`
- API Docs: http://127.0.0.1:5000/api/docs

## Summary

✅ **What's New:**
- `mtpl_leave_allotment` table for storing allocations
- New API endpoints for CRUD operations
- Bulk assign and default assign features
- Decimal support for half-day leaves
- Audit trail (who assigned, when)

✅ **What Changed:**
- Frontend now uses `/api/leave-allotments` instead of `/api/user-leave-balance`
- Employee balance fetched from allotment table
- Admin can assign to multiple users at once

✅ **What Stayed Same:**
- Leave types management
- Leave request workflow
- Approval/rejection process
- UI/UX remains identical

---

**Last Updated:** 2024
**Version:** 1.0
