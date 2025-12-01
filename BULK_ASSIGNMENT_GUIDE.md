# Bulk Leave Assignment Guide

## Overview
The system now supports **bulk leave balance assignment** to multiple employees at once, saving time when managing leave quotas for your organization.

## Features Added

### 1. Bulk Leave Balance Assignment
- Assign the same leave balance to multiple employees simultaneously
- Select all employees with one click
- Clear selection easily
- Real-time feedback on assignment success

### 2. User Management
- View all users from `mtpl_users` table (not just biometric-registered users)
- Assign leaves to any active user in the system
- No need for face registration to assign leave balances

## How to Use

### Access the Feature
1. Navigate to **Leave Management** page: `http://127.0.0.1:5000/leave-management`
2. Go to **Admin Panel** tab
3. Scroll down to **Bulk Assign Leave Balance** section

### Assign Leaves to Multiple Employees

#### Step 1: Select Employees
- **Multi-select dropdown**: Hold `Ctrl` (Windows) or `Cmd` (Mac) and click to select multiple employees
- **Select All button**: Click to select all employees at once
- **Clear button**: Click to deselect all employees

#### Step 2: Configure Leave Details
- **Leave Type**: Choose the type of leave (Casual, Sick, etc.)
- **Total Leaves**: Enter the number of leaves (supports decimals like 12.5)
- **Year**: Specify the year for the leave quota

#### Step 3: Assign
- Click **Assign to Selected Employees** button
- System will assign the specified leave balance to all selected employees
- Success message shows the number of employees updated

## API Endpoint

### Bulk Assignment API
```
POST /api/user-leave-balance/bulk
```

**Request Body:**
```json
{
  "user_ids": [1, 2, 3, 4, 5],
  "leave_type_id": 1,
  "total": 12,
  "year": 2024
}
```

**Response:**
```json
{
  "success": true,
  "count": 5,
  "balances": [
    {
      "id": 1,
      "user_id": 1,
      "leave_type_id": 1,
      "leave_type_name": "Casual Leave",
      "total": 12,
      "used": 0,
      "remaining": 12,
      "year": 2024
    },
    ...
  ]
}
```

## Example Use Cases

### 1. Annual Leave Allocation
Assign 12 casual leaves to all employees at the start of the year:
- Select all employees
- Choose "Casual Leave"
- Enter 12 in total leaves
- Set year to 2024
- Click assign

### 2. Department-wise Assignment
Assign 10 sick leaves to specific department employees:
- Select employees from a specific department
- Choose "Sick Leave"
- Enter 10 in total leaves
- Click assign

### 3. Mid-year Adjustment
Update leave balance for multiple employees:
- Select affected employees
- Choose leave type
- Enter new total (system will update existing records)
- Click assign

## Technical Details

### Database Updates
- If a user already has a leave balance for the specified type and year, it will be **updated**
- If no balance exists, a new record will be **created**
- All updates happen in a single transaction for data consistency

### Validation
- At least one employee must be selected
- Leave type and total are required fields
- Year defaults to current year if not specified

### Performance
- Bulk operation processes all users in one database transaction
- Efficient for large employee counts
- Returns count of successfully updated records

## Benefits

✅ **Time-saving**: Assign leaves to 100+ employees in seconds  
✅ **Consistent**: Same leave quota applied to all selected employees  
✅ **Flexible**: Update existing balances or create new ones  
✅ **User-friendly**: Simple interface with select all/clear options  
✅ **Reliable**: Transaction-based updates ensure data integrity  

## Notes

- Users don't need face registration to receive leave assignments
- Leave balances are year-specific (separate quotas per year)
- Existing balances are updated, not added to
- Decimal values supported (e.g., 0.5 for half-day leaves)

## Troubleshooting

**Issue**: No users showing in dropdown  
**Solution**: Ensure users exist in `mtpl_users` table with `userIsActive='1'`

**Issue**: Assignment fails  
**Solution**: Check that leave type exists and is active

**Issue**: Can't select multiple users  
**Solution**: Hold Ctrl (Windows) or Cmd (Mac) while clicking, or use "Select All" button

## Related Documentation
- `LEAVE_MANAGEMENT_GUIDE.md` - Complete leave system guide
- `API_DOCUMENTATION.md` - Full API reference
- `README.md` - System overview
