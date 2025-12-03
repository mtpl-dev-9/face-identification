# Leave Management System - Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        WEB BROWSER                               │
│  http://127.0.0.1:5000/leave-management                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTP Requests
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FLASK APPLICATION                            │
│                        (app.py)                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    VIEW ROUTES                            │  │
│  │  • GET /leave-management → leave_management.html         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API ROUTES                             │  │
│  │                                                            │  │
│  │  Leave Types:                                             │  │
│  │  • GET    /api/leave-types                               │  │
│  │  • POST   /api/leave-types                               │  │
│  │  • DELETE /api/leave-types/{id}                          │  │
│  │                                                            │  │
│  │  Leave Balance:                                           │  │
│  │  • GET    /api/user-leave-balance                        │  │
│  │  • POST   /api/user-leave-balance                        │  │
│  │                                                            │  │
│  │  Leave Requests:                                          │  │
│  │  • GET    /api/leave-requests                            │  │
│  │  • POST   /api/leave-requests                            │  │
│  │  • POST   /api/leave-requests/{id}/approve               │  │
│  │  • POST   /api/leave-requests/{id}/reject                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ SQLAlchemy ORM
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MODELS (models.py)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │   LeaveType      │  │ UserLeaveBalance │  │LeaveRequest  │ │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────┤ │
│  │ • id             │  │ • id             │  │ • id         │ │
│  │ • name           │  │ • user_id        │  │ • user_id    │ │
│  │ • is_active      │  │ • leave_type_id  │  │ • leave_type │ │
│  │ • created_at     │  │ • total          │  │ • from_date  │ │
│  │                  │  │ • used           │  │ • to_date    │ │
│  │ Methods:         │  │ • year           │  │ • days       │ │
│  │ • to_dict()      │  │                  │  │ • reason     │ │
│  │                  │  │ Properties:      │  │ • status     │ │
│  │                  │  │ • remaining      │  │ • approved_by│ │
│  │                  │  │                  │  │              │ │
│  │                  │  │ Methods:         │  │ Methods:     │ │
│  │                  │  │ • to_dict()      │  │ • to_dict()  │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
│                                                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ SQL Queries
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   MySQL DATABASE                                 │
│                   (mtpl_website)                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              mtpl_leave_types                             │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ leaveTypeId (PK) | leaveTypeName | leaveTypeIsActive     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           mtpl_user_leave_balance                         │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ balanceId (PK) | balanceUserId | balanceLeaveTypeId (FK) │  │
│  │ balanceTotal | balanceUsed | balanceYear                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            mtpl_leave_requests                            │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ leaveRequestId (PK) | leaveRequestUserId                 │  │
│  │ leaveRequestLeaveTypeId (FK) | leaveRequestFromDate      │  │
│  │ leaveRequestToDate | leaveRequestDays | leaveRequestReason│ │
│  │ leaveRequestStatus | leaveRequestApprovedBy              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              mtpl_users (existing)                        │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ userId (PK) | userFirstName | userLastName | userLogin   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### 1. Admin Creates Leave Type

```
Admin (Browser)
    │
    │ POST /api/leave-types
    │ {"name": "Casual Leave"}
    ▼
Flask Route (app.py)
    │
    │ Validate name
    │ Check duplicates
    ▼
LeaveType Model
    │
    │ Create instance
    │ db.session.add()
    ▼
MySQL Database
    │
    │ INSERT INTO mtpl_leave_types
    ▼
Response
    │
    │ {"success": true, "leave_type": {...}}
    ▼
Browser (Update UI)
```

### 2. Admin Assigns Leave Balance

```
Admin (Browser)
    │
    │ POST /api/user-leave-balance
    │ {"user_id": 1, "leave_type_id": 1, "total": 12, "year": 2024}
    ▼
Flask Route (app.py)
    │
    │ Validate inputs
    │ Check if balance exists
    ▼
UserLeaveBalance Model
    │
    │ Create/Update instance
    │ db.session.add()
    ▼
MySQL Database
    │
    │ INSERT/UPDATE mtpl_user_leave_balance
    ▼
Response
    │
    │ {"success": true, "balance": {...}}
    ▼
Browser (Show success)
```

### 3. Employee Requests Leave

```
Employee (Browser)
    │
    │ POST /api/leave-requests
    │ {"user_id": 1, "leave_type_id": 1, "from_date": "2024-12-25", 
    │  "to_date": "2024-12-27", "reason": "Family wedding"}
    ▼
Flask Route (app.py)
    │
    │ Calculate days: (to_date - from_date) + 1 = 3
    │ Query UserLeaveBalance
    ▼
Validation
    │
    │ Check: remaining >= requested_days
    │ 10 >= 3 ✅
    ▼
LeaveRequest Model
    │
    │ Create instance with status="pending"
    │ db.session.add()
    ▼
MySQL Database
    │
    │ INSERT INTO mtpl_leave_requests
    ▼
Response
    │
    │ {"success": true, "request": {...}}
    ▼
Browser (Show success)
```

### 4. Admin Approves Leave Request

```
Admin (Browser)
    │
    │ POST /api/leave-requests/1/approve
    │ {"approved_by": 1}
    ▼
Flask Route (app.py)
    │
    │ Query LeaveRequest by ID
    │ Check status == "pending"
    ▼
Validation
    │
    │ Query UserLeaveBalance
    │ Check: remaining >= request.days
    ▼
Update Models
    │
    ├─► LeaveRequest
    │   │ status = "approved"
    │   │ approved_by = 1
    │   │ approved_at = now()
    │   
    └─► UserLeaveBalance
        │ used += request.days
        │ (remaining auto-calculated)
    ▼
MySQL Database
    │
    │ UPDATE mtpl_leave_requests
    │ UPDATE mtpl_user_leave_balance
    ▼
Response
    │
    │ {"success": true, "request": {...}}
    ▼
Browser (Update UI, show approved)
```

## Component Interaction

```
┌──────────────┐
│   Browser    │
│   (Client)   │
└──────┬───────┘
       │
       │ HTTP/JSON
       │
┌──────▼───────┐      ┌──────────────┐
│    Flask     │◄────►│   Models     │
│   Routes     │      │  (ORM Layer) │
└──────┬───────┘      └──────┬───────┘
       │                     │
       │                     │ SQL
       │                     │
       │              ┌──────▼───────┐
       │              │    MySQL     │
       │              │   Database   │
       │              └──────────────┘
       │
       │ Render
       │
┌──────▼───────┐
│  Templates   │
│   (Jinja2)   │
└──────────────┘
```

## Security & Validation Flow

```
Request
  │
  ├─► Input Validation
  │   ├─ Required fields present?
  │   ├─ Data types correct?
  │   └─ Date format valid?
  │
  ├─► Business Logic Validation
  │   ├─ User exists?
  │   ├─ Leave type active?
  │   ├─ Balance sufficient?
  │   └─ Date range valid?
  │
  ├─► Database Constraints
  │   ├─ Foreign keys valid?
  │   ├─ Unique constraints?
  │   └─ NOT NULL constraints?
  │
  └─► Response
      ├─ Success: 200 + data
      └─ Error: 400/404 + message
```

## State Machine: Leave Request Status

```
┌─────────┐
│  START  │
└────┬────┘
     │
     │ Employee creates request
     ▼
┌─────────┐
│ PENDING │◄──────────────────┐
└────┬────┘                   │
     │                        │
     ├─► Admin approves       │ Admin can change
     │   ┌──────────┐         │ before approval
     │   │ APPROVED │         │
     │   └──────────┘         │
     │                        │
     └─► Admin rejects        │
         ┌──────────┐         │
         │ REJECTED │─────────┘
         └──────────┘
```

## Database Relationships

```
mtpl_users
    │
    │ 1:N
    ▼
mtpl_user_leave_balance ◄─── N:1 ─── mtpl_leave_types
    │                                      │
    │ 1:N                                  │ 1:N
    ▼                                      ▼
mtpl_leave_requests ◄──────── N:1 ────────┘
```

## Technology Stack

```
┌─────────────────────────────────────┐
│         Frontend Layer              │
├─────────────────────────────────────┤
│ • HTML5 (Jinja2 Templates)          │
│ • Bootstrap 5 (UI Framework)        │
│ • JavaScript (Vanilla)              │
│ • Fetch API (AJAX Requests)         │
└─────────────────────────────────────┘
                 │
                 │ HTTP/JSON
                 ▼
┌─────────────────────────────────────┐
│         Backend Layer               │
├─────────────────────────────────────┤
│ • Python 3                          │
│ • Flask (Web Framework)             │
│ • SQLAlchemy (ORM)                  │
│ • PyMySQL (Database Driver)         │
│ • PyTZ (Timezone Support)           │
└─────────────────────────────────────┘
                 │
                 │ SQL
                 ▼
┌─────────────────────────────────────┐
│         Database Layer              │
├─────────────────────────────────────┤
│ • MySQL 5.7+                        │
│ • InnoDB Engine                     │
│ • UTF8MB4 Charset                   │
│ • Foreign Key Constraints           │
└─────────────────────────────────────┘
```

## File Structure

```
face_a/
│
├── app.py                          # Flask routes & business logic
│   ├── View Routes
│   │   └── /leave-management
│   └── API Routes
│       ├── /api/leave-types/*
│       ├── /api/user-leave-balance
│       └── /api/leave-requests/*
│
├── models.py                       # SQLAlchemy models
│   ├── LeaveType
│   ├── UserLeaveBalance
│   └── LeaveRequest
│
├── templates/
│   └── leave_management.html       # UI with 3 tabs
│       ├── Admin Panel
│       ├── Employee Panel
│       └── Leave Requests
│
├── leave_management_schema.sql     # Database schema
│
└── Documentation/
    ├── LEAVE_MANAGEMENT_GUIDE.md
    ├── LEAVE_QUICK_START.md
    └── LEAVE_SYSTEM_ARCHITECTURE.md (this file)
```

## API Request/Response Examples

### Create Leave Type
```
Request:
POST /api/leave-types
Content-Type: application/json

{
  "name": "Casual Leave"
}

Response:
{
  "success": true,
  "leave_type": {
    "id": 1,
    "name": "Casual Leave",
    "is_active": true,
    "created_at": "2024-12-20T10:30:00Z"
  }
}
```

### Assign Leave Balance
```
Request:
POST /api/user-leave-balance
Content-Type: application/json

{
  "user_id": 1,
  "leave_type_id": 1,
  "total": 12,
  "year": 2024
}

Response:
{
  "success": true,
  "balance": {
    "id": 1,
    "user_id": 1,
    "leave_type_id": 1,
    "leave_type_name": "Casual Leave",
    "total": 12,
    "used": 0,
    "remaining": 12,
    "year": 2024
  }
}
```

### Request Leave
```
Request:
POST /api/leave-requests
Content-Type: application/json

{
  "user_id": 1,
  "leave_type_id": 1,
  "from_date": "2024-12-25",
  "to_date": "2024-12-27",
  "reason": "Family wedding"
}

Response:
{
  "success": true,
  "request": {
    "id": 1,
    "user_id": 1,
    "user_name": "John Doe",
    "leave_type_id": 1,
    "leave_type_name": "Casual Leave",
    "from_date": "2024-12-25",
    "to_date": "2024-12-27",
    "days": 3,
    "reason": "Family wedding",
    "status": "pending",
    "approved_by": null,
    "approved_at": null,
    "created_at": "2024-12-20T10:30:00Z"
  }
}
```

## Performance Considerations

### Database Indexes
```sql
-- Optimized queries with indexes
INDEX idx_user_year ON mtpl_user_leave_balance (balanceUserId, balanceYear)
INDEX idx_user ON mtpl_leave_requests (leaveRequestUserId)
INDEX idx_status ON mtpl_leave_requests (leaveRequestStatus)
INDEX idx_dates ON mtpl_leave_requests (leaveRequestFromDate, leaveRequestToDate)
```

### Query Optimization
- Use SQLAlchemy relationships for JOIN queries
- Filter by indexed columns
- Limit result sets with pagination
- Use eager loading for related data

## Scalability

### Current Capacity
- Supports unlimited leave types
- Supports unlimited employees
- Supports unlimited requests
- Year-wise data partitioning

### Future Enhancements
- Add caching layer (Redis)
- Implement pagination for large datasets
- Add background jobs for notifications
- Archive old leave data

---

**Architecture Version:** 1.0  
**Last Updated:** December 2024  
**Status:** Production Ready
