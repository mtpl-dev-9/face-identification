# Leave Allotment System Guide

## Overview

The Leave Allotment System uses the `mtpl_leave_allotment` table to store leave allocations for employees. This table tracks how many leaves are assigned to each user for different leave types per year.

## Database Structure

### Table: `mtpl_leave_allotment`

| Column | Type | Description |
|--------|------|-------------|
| `allotmentId` | INT | Primary key, auto-increment |
| `allotmentUserId` | INT | User ID (references mtpl_users) |
| `allotmentLeaveTypeId` | INT | Leave type ID (references mtpl_leave_types) |
| `allotmentTotal` | DECIMAL(5,1) | Total leaves allocated (supports decimals like 0.5, 12.5) |
| `allotmentYear` | INT | Year for which leaves are allocated |
| `allotmentAssignedBy` | INT | User ID who assigned the leaves |
| `allotmentAssignedAt` | DATETIME | When the allocation was created |
| `allotmentUpdatedAt` | DATETIME | Last update timestamp |

### Example Data

```sql
-- User 1 has 4 Casual Leaves, 7 Sick Leaves, and 0.5 Celebratory Leave for 2024
INSERT INTO mtpl_leave_allotment 
(allotmentUserId, allotmentLeaveTypeId, allotmentTotal, allotmentYear, allotmentAssignedBy)
VALUES 
(1, 1, 4, 2024, 1),    -- 4 Casual Leaves
(1, 2, 7, 2024, 1),    -- 7 Sick Leaves
(1, 3, 0.5, 2024, 1);  -- 0.5 Celebratory Leave
```

## Setup Instructions

### 1. Initialize Database

Run the SQL schema:

```bash
mysql -u admin -p mtpl_website < leave_allotment_schema.sql
```

Or run the Python initialization script:

```bash
python init_leave_allotment.py
```

### 2. Access Leave Management

Navigate to: **http://127.0.0.1:5000/leave-management**

## Features

### 1. Assign Leave Balance (Individual)

Assign leaves to a single employee:

- Select Employee
- Select Leave Type (Casual, Sick, Celebratory)
- Enter Total Leaves (supports decimals: 0.5, 12.5, etc.)
- Enter Year (default: current year)
- Click "Assign Balance"

**API Endpoint:**
```
POST /api/leave-allotments
Body: {
  "user_id": 1,
  "leave_type_id": 1,
  "total": 4,
  "year": 2024,
  "assigned_by": 1
}
```

### 2. Bulk Assign Leave Balance

Assign leaves to multiple employees at once:

- Select multiple employees (Ctrl+Click or Shift+Click)
- Select Leave Type
- Enter Total Leaves
- Enter Year
- Click "Assign"

**API Endpoint:**
```
POST /api/leave-allotments/bulk
Body: {
  "user_ids": [1, 2, 3],
  "leave_type_id": 1,
  "total": 4,
  "year": 2024,
  "assigned_by": 1
}
```

### 3. Assign Default Leaves

Assign default leave allocations to ALL active users:

- Set Casual Leave (default: 4)
- Set Sick Leave (default: 7)
- Set Celebratory Leave (default: 0.5)
- Enter Year
- Click "Assign to All Users"

This will create/update leave allotments for all active users in the system.

**API Endpoint:**
```
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

### 4. View Employee Leave Balance

Employees can view their allocated leaves:

- Go to "Employee Panel" tab
- Select Employee
- View leave balance showing:
  - Leave Type Name
  - Total Allocated
  - Used (currently 0, will be updated when leaves are approved)
  - Remaining

**API Endpoint:**
```
GET /api/leave-allotments?user_id=1&year=2024
```

## API Reference

### Get Leave Allotments

```http
GET /api/leave-allotments?user_id={user_id}&year={year}
```

**Response:**
```json
{
  "success": true,
  "allotments": [
    {
      "id": 1,
      "user_id": 1,
      "user_name": "John Doe",
      "leave_type_id": 1,
      "leave_type_name": "Casual Leave",
      "total": 4.0,
      "year": 2024,
      "assigned_by": 1,
      "assigned_by_name": "Admin User",
      "assigned_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:00:00Z"
    }
  ]
}
```

### Create Leave Allotment

```http
POST /api/leave-allotments
Content-Type: application/json

{
  "user_id": 1,
  "leave_type_id": 1,
  "total": 4,
  "year": 2024,
  "assigned_by": 1
}
```

### Bulk Create Leave Allotments

```http
POST /api/leave-allotments/bulk
Content-Type: application/json

{
  "user_ids": [1, 2, 3],
  "leave_type_id": 1,
  "total": 4,
  "year": 2024,
  "assigned_by": 1
}
```

### Assign Default Leaves

```http
POST /api/leave-allotments/default
Content-Type: application/json

{
  "year": 2024,
  "defaults": {
    "casual": 4,
    "sick": 7,
    "celebratory": 0.5
  },
  "assigned_by": 1
}
```

### Delete Leave Allotment

```http
DELETE /api/leave-allotments/{allotment_id}
```

## Database Queries

### View All Allotments

```sql
SELECT 
  a.allotmentId,
  u.userFirstName,
  u.userLastName,
  lt.leaveTypeName,
  a.allotmentTotal,
  a.allotmentYear
FROM mtpl_leave_allotment a
JOIN mtpl_users u ON a.allotmentUserId = u.userId
JOIN mtpl_leave_types lt ON a.allotmentLeaveTypeId = lt.leaveTypeId
ORDER BY a.allotmentYear DESC, u.userFirstName;
```

### View User's Leave Balance

```sql
SELECT 
  lt.leaveTypeName,
  a.allotmentTotal,
  a.allotmentYear
FROM mtpl_leave_allotment a
JOIN mtpl_leave_types lt ON a.allotmentLeaveTypeId = lt.leaveTypeId
WHERE a.allotmentUserId = 1 AND a.allotmentYear = 2024;
```

### Count Allotments by Year

```sql
SELECT 
  allotmentYear,
  COUNT(*) as total_allotments,
  COUNT(DISTINCT allotmentUserId) as unique_users
FROM mtpl_leave_allotment
GROUP BY allotmentYear
ORDER BY allotmentYear DESC;
```

### Find Users Without Leave Allotments

```sql
SELECT 
  u.userId,
  u.userFirstName,
  u.userLastName
FROM mtpl_users u
WHERE u.userIsActive = '1'
AND u.userId NOT IN (
  SELECT DISTINCT allotmentUserId 
  FROM mtpl_leave_allotment 
  WHERE allotmentYear = 2024
);
```

## Workflow Example

### Scenario: Assign leaves to all employees for 2024

1. **Initialize System**
   ```bash
   python init_leave_allotment.py
   ```

2. **Access Leave Management**
   - Open browser: http://127.0.0.1:5000/leave-management
   - Go to "Admin Panel" tab

3. **Assign Default Leaves**
   - Set Casual: 4
   - Set Sick: 7
   - Set Celebratory: 0.5
   - Year: 2024
   - Click "Assign to All Users"

4. **Verify in Database**
   ```sql
   SELECT COUNT(*) FROM mtpl_leave_allotment WHERE allotmentYear = 2024;
   ```

5. **View Employee Balance**
   - Go to "Employee Panel" tab
   - Select an employee
   - See their leave balance displayed

## Troubleshooting

### Issue: Allotments not showing in database

**Solution:** Check if the table exists:
```sql
SHOW TABLES LIKE 'mtpl_leave_allotment';
```

If not, run:
```bash
mysql -u admin -p mtpl_website < leave_allotment_schema.sql
```

### Issue: Cannot assign leaves

**Solution:** Ensure leave types exist:
```sql
SELECT * FROM mtpl_leave_types;
```

If empty, run:
```bash
python init_leave_allotment.py
```

### Issue: Decimal values not working

**Solution:** The `allotmentTotal` column is DECIMAL(5,1), supporting values like:
- 0.5 (half day)
- 4.0 (4 days)
- 12.5 (12.5 days)

Make sure you're using the correct format.

## Best Practices

1. **Yearly Allocation**: Assign leaves at the beginning of each year
2. **Backup Data**: Before bulk operations, backup the database
3. **Audit Trail**: The system tracks who assigned leaves and when
4. **Decimal Support**: Use 0.5 for half-day leaves
5. **Update vs Create**: The system automatically updates existing allotments

## Support

For issues or questions:
- Check the database schema: `leave_allotment_schema.sql`
- Review the model: `models.py` → `LeaveAllotment` class
- Check API endpoints: `app.py` → `/api/leave-allotments/*`
- View frontend: `templates/leave_management.html`
