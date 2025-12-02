# Leave Allotment System - Visual Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    LEAVE ALLOTMENT SYSTEM                        │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   ADMIN      │         │   EMPLOYEE   │         │   DATABASE   │
│   PANEL      │         │   PANEL      │         │              │
└──────┬───────┘         └──────┬───────┘         └──────┬───────┘
       │                        │                        │
       │ 1. Assign Leaves       │                        │
       ├────────────────────────┼───────────────────────>│
       │                        │                        │
       │                        │ 2. View Balance        │
       │                        ├───────────────────────>│
       │                        │                        │
       │                        │ 3. Return Data         │
       │                        │<───────────────────────┤
       │                        │                        │
       │                        │ Display:               │
       │                        │ Casual: 4 | Used: 0   │
       │                        │ Sick: 7 | Used: 0     │
       │                        │ Celebratory: 0.5      │
       │                        │                        │
```

## Database Schema

```
┌─────────────────────────────────────────────────────────────────┐
│                    mtpl_leave_allotment                          │
├──────────────────┬──────────────┬──────────────────────────────┤
│ allotmentId      │ INT          │ Primary Key                  │
│ allotmentUserId  │ INT          │ → mtpl_users.userId          │
│ allotmentLeaveTypeId │ INT      │ → mtpl_leave_types.leaveTypeId│
│ allotmentTotal   │ DECIMAL(5,1) │ Total leaves (4, 0.5, 12.5)  │
│ allotmentYear    │ INT          │ Year (2024, 2025)            │
│ allotmentAssignedBy │ INT       │ Who assigned                 │
│ allotmentAssignedAt │ DATETIME  │ When assigned                │
│ allotmentUpdatedAt  │ DATETIME  │ Last update                  │
└──────────────────┴──────────────┴──────────────────────────────┘
```

## Data Flow

### 1. Assign Leave (Single User)

```
Admin Interface
     │
     ├─ Select User: John Doe (ID: 1)
     ├─ Select Leave Type: Casual Leave (ID: 1)
     ├─ Enter Total: 4
     ├─ Enter Year: 2024
     │
     ▼
POST /api/leave-allotments
{
  "user_id": 1,
  "leave_type_id": 1,
  "total": 4,
  "year": 2024,
  "assigned_by": 1
}
     │
     ▼
Database Insert/Update
INSERT INTO mtpl_leave_allotment 
(allotmentUserId, allotmentLeaveTypeId, allotmentTotal, allotmentYear, allotmentAssignedBy)
VALUES (1, 1, 4, 2024, 1);
     │
     ▼
Success Response
{
  "success": true,
  "allotment": {
    "id": 1,
    "user_id": 1,
    "user_name": "John Doe",
    "leave_type_name": "Casual Leave",
    "total": 4,
    "year": 2024
  }
}
```

### 2. Bulk Assign (Multiple Users)

```
Admin Interface
     │
     ├─ Select Users: [1, 2, 3]
     ├─ Select Leave Type: Sick Leave (ID: 2)
     ├─ Enter Total: 7
     ├─ Enter Year: 2024
     │
     ▼
POST /api/leave-allotments/bulk
{
  "user_ids": [1, 2, 3],
  "leave_type_id": 2,
  "total": 7,
  "year": 2024,
  "assigned_by": 1
}
     │
     ▼
Database Batch Insert
For each user_id in [1, 2, 3]:
  INSERT INTO mtpl_leave_allotment ...
     │
     ▼
Success Response
{
  "success": true,
  "count": 3,
  "allotments": [...]
}
```

### 3. Assign Default Leaves (All Users)

```
Admin Interface
     │
     ├─ Casual: 4
     ├─ Sick: 7
     ├─ Celebratory: 0.5
     ├─ Year: 2024
     │
     ▼
POST /api/leave-allotments/default
{
  "year": 2024,
  "defaults": {
    "casual": 4,
    "sick": 7,
    "celebratory": 0.5
  },
  "assigned_by": 1
}
     │
     ▼
Database Batch Insert
For each active user:
  For each leave type (Casual, Sick, Celebratory):
    INSERT INTO mtpl_leave_allotment ...
     │
     ▼
Result: 3 records per user
If 10 users → 30 records created
```

### 4. View Employee Balance

```
Employee Interface
     │
     ├─ Select User: John Doe (ID: 1)
     │
     ▼
GET /api/leave-allotments?user_id=1&year=2024
     │
     ▼
Database Query
SELECT * FROM mtpl_leave_allotment 
WHERE allotmentUserId = 1 AND allotmentYear = 2024;
     │
     ▼
Response
{
  "success": true,
  "allotments": [
    {
      "leave_type_name": "Casual Leave",
      "total": 4,
      "year": 2024
    },
    {
      "leave_type_name": "Sick Leave",
      "total": 7,
      "year": 2024
    },
    {
      "leave_type_name": "Celebratory Leave",
      "total": 0.5,
      "year": 2024
    }
  ]
}
     │
     ▼
Display on UI
┌─────────────────────────────┐
│ Casual Leave                │
│ Total: 4 | Used: 0 | Rem: 4 │
├─────────────────────────────┤
│ Sick Leave                  │
│ Total: 7 | Used: 0 | Rem: 7 │
├─────────────────────────────┤
│ Celebratory Leave           │
│ Total: 0.5 | Used: 0 | Rem: 0.5│
└─────────────────────────────┘
```

## Example Data Structure

### Sample Records in Database

```
┌─────┬────────┬──────────┬───────┬──────┬────────────┬─────────────────────┐
│ ID  │ UserID │ LeaveType│ Total │ Year │ AssignedBy │ AssignedAt          │
├─────┼────────┼──────────┼───────┼──────┼────────────┼─────────────────────┤
│ 1   │ 1      │ 1        │ 4.0   │ 2024 │ 1          │ 2024-01-01 10:00:00 │
│ 2   │ 1      │ 2        │ 7.0   │ 2024 │ 1          │ 2024-01-01 10:00:00 │
│ 3   │ 1      │ 3        │ 0.5   │ 2024 │ 1          │ 2024-01-01 10:00:00 │
│ 4   │ 2      │ 1        │ 4.0   │ 2024 │ 1          │ 2024-01-01 10:00:00 │
│ 5   │ 2      │ 2        │ 7.0   │ 2024 │ 1          │ 2024-01-01 10:00:00 │
│ 6   │ 2      │ 3        │ 0.5   │ 2024 │ 1          │ 2024-01-01 10:00:00 │
└─────┴────────┴──────────┴───────┴──────┴────────────┴─────────────────────┘

Legend:
- UserID 1 = John Doe
- UserID 2 = Jane Smith
- LeaveType 1 = Casual Leave
- LeaveType 2 = Sick Leave
- LeaveType 3 = Celebratory Leave
```

## API Endpoint Map

```
┌─────────────────────────────────────────────────────────────────┐
│                      API ENDPOINTS                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  GET /api/leave-allotments                                       │
│  ├─ Query: user_id, year                                         │
│  └─ Returns: List of allotments                                  │
│                                                                  │
│  POST /api/leave-allotments                                      │
│  ├─ Body: user_id, leave_type_id, total, year, assigned_by      │
│  └─ Returns: Created allotment                                   │
│                                                                  │
│  POST /api/leave-allotments/bulk                                 │
│  ├─ Body: user_ids[], leave_type_id, total, year, assigned_by   │
│  └─ Returns: Count and list of allotments                        │
│                                                                  │
│  POST /api/leave-allotments/default                              │
│  ├─ Body: year, defaults{casual, sick, celebratory}, assigned_by│
│  └─ Returns: Count and users affected                            │
│                                                                  │
│  DELETE /api/leave-allotments/{id}                               │
│  ├─ Param: allotment_id                                          │
│  └─ Returns: Success status                                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMPLETE WORKFLOW                             │
└─────────────────────────────────────────────────────────────────┘

1. INITIALIZATION
   ┌──────────────────┐
   │ Run SQL Schema   │
   └────────┬─────────┘
            │
   ┌────────▼─────────┐
   │ Create Tables    │
   └────────┬─────────┘
            │
   ┌────────▼─────────┐
   │ Init Leave Types │
   └────────┬─────────┘
            │
            ▼

2. ASSIGNMENT
   ┌──────────────────┐
   │ Admin Assigns    │
   │ Leaves           │
   └────────┬─────────┘
            │
   ┌────────▼─────────┐
   │ Data Stored in   │
   │ mtpl_leave_      │
   │ allotment        │
   └────────┬─────────┘
            │
            ▼

3. VIEWING
   ┌──────────────────┐
   │ Employee Views   │
   │ Balance          │
   └────────┬─────────┘
            │
   ┌────────▼─────────┐
   │ Fetch from DB    │
   └────────┬─────────┘
            │
   ┌────────▼─────────┐
   │ Display on UI    │
   └──────────────────┘

4. REQUESTING
   ┌──────────────────┐
   │ Employee Requests│
   │ Leave            │
   └────────┬─────────┘
            │
   ┌────────▼─────────┐
   │ Check Balance    │
   │ from Allotment   │
   └────────┬─────────┘
            │
   ┌────────▼─────────┐
   │ Create Request   │
   └────────┬─────────┘
            │
            ▼

5. APPROVAL
   ┌──────────────────┐
   │ Admin Approves   │
   └────────┬─────────┘
            │
   ┌────────▼─────────┐
   │ Update Used      │
   │ in Balance Table │
   └──────────────────┘
```

## File Structure

```
face_a/
│
├── Database Layer
│   ├── models.py (LeaveAllotment model)
│   └── leave_allotment_schema.sql
│
├── Backend Layer
│   ├── app.py (API endpoints)
│   └── database.py
│
├── Frontend Layer
│   └── templates/leave_management.html
│
├── Initialization
│   └── init_leave_allotment.py
│
├── Testing
│   └── test_leave_allotment.py
│
└── Documentation
    ├── LEAVE_ALLOTMENT_GUIDE.md
    ├── LEAVE_ALLOTMENT_CHANGES.md
    ├── QUICK_START_LEAVE_ALLOTMENT.md
    └── LEAVE_ALLOTMENT_DIAGRAM.md (this file)
```

## Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                         KEY POINTS                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ✓ Table: mtpl_leave_allotment                                   │
│  ✓ Stores: User allocations per year                             │
│  ✓ Supports: Decimals (0.5, 12.5)                                │
│  ✓ Features: Single, Bulk, Default assign                        │
│  ✓ Audit: Tracks who assigned and when                           │
│  ✓ API: RESTful endpoints                                        │
│  ✓ UI: Admin and Employee panels                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```
