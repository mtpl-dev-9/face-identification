# Leave Management System - Complete Guide

## Overview

A comprehensive leave management system integrated with the Face Recognition Attendance System. Admins can create dynamic leave types, assign leave balances to employees, and approve/reject leave requests.

## Features

### ✅ Dynamic Leave Types
- Create unlimited leave types (Casual, Sick, Celebratory, etc.)
- Activate/deactivate leave types
- No code changes needed

### ✅ Leave Balance Management
- Admin assigns leave balance to each employee
- Track total, used, and remaining leaves
- Year-wise leave tracking
- Automatic balance deduction on approval

### ✅ Leave Request System
- Employees request leaves with date range
- Automatic calculation of leave days
- Validates against available balance
- Reason/notes support

### ✅ Approval Workflow
- Pending/Approved/Rejected status
- Admin approval/rejection
- Tracks who approved and when
- Filter requests by status

## Database Schema

### Tables Created

1. **mtpl_leave_types** - Stores leave type definitions
2. **mtpl_user_leave_balance** - Tracks employee leave balances
3. **mtpl_leave_requests** - Stores leave requests

## Setup Instructions

### Step 1: Run SQL Migration

Execute the SQL file to create tables:

```bash
mysql -u root -p mtpl_website < leave_management_schema.sql
```

Or manually run the SQL in phpMyAdmin/MySQL Workbench.

### Step 2: Restart Flask Application

```bash
python app.py
```

### Step 3: Access Leave Management

Navigate to: **http://127.0.0.1:5000/leave-management**

## Usage Guide

### For Admins

#### 1. Create Leave Types

1. Go to **Leave Management** → **Admin Panel**
2. Enter leave type name (e.g., "Casual Leave")
3. Click **Add**
4. Repeat for all leave types:
   - Casual Leave
   - Sick Leave
   - Celebratory Leave
   - Earned Leave
   - Maternity Leave
   - Paternity Leave

#### 2. Assign Leave Balance

1. Select **Employee** from dropdown
2. Select **Leave Type**
3. Enter **Total Leaves** (e.g., 12)
4. Enter **Year** (e.g., 2024)
5. Click **Assign Balance**

**Example:**
- Employee: John Doe
- Leave Type: Casual Leave
- Total: 12 leaves
- Year: 2024

#### 3. Approve/Reject Requests

1. Go to **Leave Requests** tab
2. Filter by status (Pending/Approved/Rejected)
3. Click ✅ to approve or ❌ to reject
4. Balance automatically deducted on approval

### For Employees

#### 1. Check Leave Balance

1. Go to **Leave Management** → **Employee Panel**
2. Select your name
3. View all leave balances:
   - Total allocated
   - Used leaves
   - Remaining leaves

#### 2. Request Leave

1. Select your name
2. Select leave type
3. Choose from date and to date
4. Enter reason (optional)
5. Click **Submit Request**

**Validation:**
- System checks if sufficient balance exists
- Calculates days automatically
- Prevents requests exceeding balance

## API Endpoints

### Leave Types

```http
GET  /api/leave-types
POST /api/leave-types
DELETE /api/leave-types/{id}
```

### Leave Balance

```http
GET  /api/user-leave-balance?user_id={id}&year={year}
POST /api/user-leave-balance
```

### Leave Requests

```http
GET  /api/leave-requests?user_id={id}&status={status}
POST /api/leave-requests
POST /api/leave-requests/{id}/approve
POST /api/leave-requests/{id}/reject
```

## API Examples

### Create Leave Type

```bash
curl -X POST http://127.0.0.1:5000/api/leave-types \
  -H "Content-Type: application/json" \
  -d '{"name": "Casual Leave"}'
```

### Assign Leave Balance

```bash
curl -X POST http://127.0.0.1:5000/api/user-leave-balance \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "leave_type_id": 1,
    "total": 12,
    "year": 2024
  }'
```

### Request Leave

```bash
curl -X POST http://127.0.0.1:5000/api/leave-requests \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "leave_type_id": 1,
    "from_date": "2024-12-25",
    "to_date": "2024-12-27",
    "reason": "Family function"
  }'
```

### Approve Leave Request

```bash
curl -X POST http://127.0.0.1:5000/api/leave-requests/1/approve \
  -H "Content-Type: application/json" \
  -d '{"approved_by": 1}'
```

## Business Logic

### Leave Calculation

- **Days = (To Date - From Date) + 1**
- Example: Dec 25 to Dec 27 = 3 days

### Balance Validation

1. Check if user has leave balance for the year
2. Check if remaining balance ≥ requested days
3. Reject if insufficient balance

### Approval Process

1. Admin approves request
2. System deducts days from balance
3. Updates `balanceUsed` field
4. Marks request as approved with timestamp

## Sample Workflow

### Scenario: Employee Requests 3 Days Casual Leave

1. **Employee Action:**
   - Selects "Casual Leave"
   - From: 2024-12-25
   - To: 2024-12-27
   - Reason: "Family wedding"
   - Submits request

2. **System Validation:**
   - Calculates: 3 days
   - Checks balance: 12 total, 2 used, 10 remaining
   - Validates: 10 ≥ 3 ✅
   - Creates request with status "pending"

3. **Admin Action:**
   - Views pending requests
   - Reviews request details
   - Clicks approve

4. **System Updates:**
   - Status: pending → approved
   - Balance used: 2 → 5
   - Remaining: 10 → 7
   - Records approval timestamp

## Reports & Analytics

### Leave Summary Report

Query to get employee leave summary:

```sql
SELECT 
  u.userFirstName,
  u.userLastName,
  lt.leaveTypeName,
  b.balanceTotal,
  b.balanceUsed,
  (b.balanceTotal - b.balanceUsed) as remaining
FROM mtpl_user_leave_balance b
JOIN mtpl_users u ON b.balanceUserId = u.userId
JOIN mtpl_leave_types lt ON b.balanceLeaveTypeId = lt.leaveTypeId
WHERE b.balanceYear = 2024
ORDER BY u.userFirstName, lt.leaveTypeName;
```

### Pending Requests Count

```sql
SELECT COUNT(*) as pending_count
FROM mtpl_leave_requests
WHERE leaveRequestStatus = 'pending';
```

### Most Used Leave Type

```sql
SELECT 
  lt.leaveTypeName,
  SUM(lr.leaveRequestDays) as total_days
FROM mtpl_leave_requests lr
JOIN mtpl_leave_types lt ON lr.leaveRequestLeaveTypeId = lt.leaveTypeId
WHERE lr.leaveRequestStatus = 'approved'
  AND YEAR(lr.leaveRequestFromDate) = 2024
GROUP BY lt.leaveTypeName
ORDER BY total_days DESC;
```

## Troubleshooting

### Issue: "Insufficient leave balance"

**Solution:** Admin needs to assign leave balance first
1. Go to Admin Panel
2. Select employee and leave type
3. Assign total leaves

### Issue: Leave types not showing

**Solution:** Create leave types first
1. Go to Admin Panel
2. Add leave types (Casual, Sick, etc.)

### Issue: Cannot approve request

**Solution:** Check if balance is sufficient
- Request might exceed available balance
- Assign more leaves or reject request

## Best Practices

1. **Annual Setup:**
   - Assign leave balances at start of year
   - Reset balances for new year

2. **Leave Policies:**
   - Casual Leave: 12 days/year
   - Sick Leave: 10 days/year
   - Celebratory Leave: 3 days/year
   - Earned Leave: 15 days/year

3. **Approval Workflow:**
   - Review requests within 24 hours
   - Check team availability before approval
   - Communicate with employee

4. **Record Keeping:**
   - Export leave reports monthly
   - Track leave patterns
   - Plan resource allocation

## Future Enhancements

- Email notifications on approval/rejection
- Leave calendar view
- Carry forward unused leaves
- Half-day leave support
- Leave encashment
- Manager hierarchy approval
- Mobile app integration

## Support

For issues or questions:
- Check database connection
- Verify SQL tables created
- Check Flask logs for errors
- Ensure user IDs exist in mtpl_users table

## License

Part of Face Recognition Attendance System - MIT License
