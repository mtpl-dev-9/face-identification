# 🏖️ Leave Management System

## Overview

A complete, dynamic leave management system integrated with the Face Recognition Attendance System. Allows admins to create unlimited leave types, assign balances to employees, and manage leave requests with approval workflow.

## ✨ Features

- ✅ **Dynamic Leave Types** - Create unlimited leave types (Casual, Sick, Celebratory, etc.)
- ✅ **Admin Controls** - Assign leave balances, approve/reject requests
- ✅ **Employee Portal** - View balance, request leaves
- ✅ **Smart Validation** - Automatic calculations, balance verification
- ✅ **Approval Workflow** - Pending → Approved/Rejected with audit trail
- ✅ **Year-wise Tracking** - Separate balances for each year
- ✅ **REST APIs** - 9 endpoints for integration
- ✅ **Responsive UI** - Works on desktop and mobile

## 🚀 Quick Start

### 1. Setup Database
```bash
mysql -u root -p mtpl_website < leave_management_schema.sql
```

### 2. Initialize System
```bash
python init_leave_system.py
```

### 3. Start Application
```bash
python app.py
```

### 4. Access System
Open: **http://127.0.0.1:5000/leave-management**

## 📖 Usage

### Admin Tasks

#### Create Leave Types
1. Go to **Admin Panel** tab
2. Enter leave type name (e.g., "Casual Leave")
3. Click **Add**

#### Assign Leave Balance
1. Select **Employee**
2. Select **Leave Type**
3. Enter **Total Leaves** (e.g., 12)
4. Enter **Year** (e.g., 2024)
5. Click **Assign Balance**

#### Approve/Reject Requests
1. Go to **Leave Requests** tab
2. Filter by **Pending**
3. Click ✅ to approve or ❌ to reject

### Employee Tasks

#### Check Leave Balance
1. Go to **Employee Panel** tab
2. Select your name
3. View: Total | Used | Remaining

#### Request Leave
1. Select your name
2. Select leave type
3. Choose from/to dates
4. Enter reason (optional)
5. Click **Submit Request**

## 🗂️ Database Tables

### mtpl_leave_types
Stores leave type definitions
- `leaveTypeId` - Primary key
- `leaveTypeName` - Leave type name (unique)
- `leaveTypeIsActive` - Active status
- `leaveTypeCreatedAt` - Creation timestamp

### mtpl_user_leave_balance
Tracks employee leave balances
- `balanceId` - Primary key
- `balanceUserId` - Employee ID
- `balanceLeaveTypeId` - Leave type ID (FK)
- `balanceTotal` - Total leaves allocated
- `balanceUsed` - Leaves used
- `balanceYear` - Year
- `balanceUpdatedAt` - Last update timestamp

### mtpl_leave_requests
Stores leave requests
- `leaveRequestId` - Primary key
- `leaveRequestUserId` - Employee ID
- `leaveRequestLeaveTypeId` - Leave type ID (FK)
- `leaveRequestFromDate` - Start date
- `leaveRequestToDate` - End date
- `leaveRequestDays` - Number of days
- `leaveRequestReason` - Reason for leave
- `leaveRequestStatus` - Status (pending/approved/rejected)
- `leaveRequestApprovedBy` - Approver ID
- `leaveRequestApprovedAt` - Approval timestamp
- `leaveRequestCreatedAt` - Creation timestamp

## 🔌 API Endpoints

### Leave Types
- `GET /api/leave-types` - List all leave types
- `POST /api/leave-types` - Create new leave type
- `DELETE /api/leave-types/{id}` - Delete leave type

### Leave Balance
- `GET /api/user-leave-balance?user_id={id}&year={year}` - Get balance
- `POST /api/user-leave-balance` - Assign/update balance

### Leave Requests
- `GET /api/leave-requests?user_id={id}&status={status}` - List requests
- `POST /api/leave-requests` - Create request
- `POST /api/leave-requests/{id}/approve` - Approve request
- `POST /api/leave-requests/{id}/reject` - Reject request

## 📊 API Examples

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

### Approve Request
```bash
curl -X POST http://127.0.0.1:5000/api/leave-requests/1/approve \
  -H "Content-Type: application/json" \
  -d '{"approved_by": 1}'
```

## 🔍 SQL Queries

### Get Employee Leave Balance
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
WHERE b.balanceYear = 2024;
```

### Get Pending Requests
```sql
SELECT 
  lr.*,
  u.userFirstName,
  u.userLastName,
  lt.leaveTypeName
FROM mtpl_leave_requests lr
JOIN mtpl_users u ON lr.leaveRequestUserId = u.userId
JOIN mtpl_leave_types lt ON lr.leaveRequestLeaveTypeId = lt.leaveTypeId
WHERE lr.leaveRequestStatus = 'pending'
ORDER BY lr.leaveRequestCreatedAt DESC;
```

### Leave Summary Report
```sql
SELECT 
  lt.leaveTypeName,
  SUM(lr.leaveRequestDays) as total_days_taken,
  COUNT(*) as total_requests
FROM mtpl_leave_requests lr
JOIN mtpl_leave_types lt ON lr.leaveRequestLeaveTypeId = lt.leaveTypeId
WHERE lr.leaveRequestStatus = 'approved'
  AND YEAR(lr.leaveRequestFromDate) = 2024
GROUP BY lt.leaveTypeName
ORDER BY total_days_taken DESC;
```

## 🎯 Workflow Example

### Scenario: Employee Requests 3 Days Casual Leave

**Step 1: Initial State**
- Employee: John Doe (ID: 1)
- Leave Type: Casual Leave (ID: 1)
- Balance: Total=12, Used=2, Remaining=10

**Step 2: Employee Creates Request**
- From: 2024-12-25
- To: 2024-12-27
- Days: 3 (auto-calculated)
- Reason: "Family wedding"
- Status: Pending

**Step 3: System Validates**
- Check balance: 10 ≥ 3 ✅
- Create request

**Step 4: Admin Approves**
- Reviews request
- Clicks approve

**Step 5: System Updates**
- Status: Pending → Approved
- Balance used: 2 → 5
- Remaining: 10 → 7
- Records approval timestamp

## ⚠️ Troubleshooting

### "Insufficient leave balance"
**Solution:** Admin needs to assign leave balance first

### Leave types not showing
**Solution:** Run `init_leave_system.py` or create manually

### Cannot approve request
**Solution:** Check if employee has sufficient balance

### Database connection error
**Solution:** Verify MySQL is running and credentials are correct

## 📚 Documentation Files

- **LEAVE_QUICK_START.md** - Quick setup guide
- **LEAVE_MANAGEMENT_GUIDE.md** - Complete usage guide
- **LEAVE_SYSTEM_ARCHITECTURE.md** - Technical architecture
- **IMPLEMENTATION_SUMMARY.md** - Implementation details
- **IMPLEMENTATION_CHECKLIST.md** - Feature checklist
- **PRESENTATION_FOR_SIR.md** - Executive summary

## 🛠️ Technical Stack

- **Backend:** Flask, SQLAlchemy
- **Database:** MySQL (mtpl_website)
- **Frontend:** Bootstrap 5, JavaScript
- **API:** RESTful JSON
- **Timezone:** IST (Indian Standard Time)

## 📋 Default Leave Types

The system comes with 6 default leave types:
1. Casual Leave
2. Sick Leave
3. Celebratory Leave
4. Earned Leave
5. Maternity Leave
6. Paternity Leave

You can add more as needed!

## 🎨 UI Screenshots

### Admin Panel
- Create and manage leave types
- Assign leave balances to employees

### Employee Panel
- View leave balance (total/used/remaining)
- Request leaves with date range

### Leave Requests
- View all requests with filters
- Approve/reject with one click
- Color-coded status badges

## 🔒 Security

- Input validation on all fields
- Balance verification before approval
- Foreign key constraints
- Audit trail for all actions
- Status validation

## 📈 Best Practices

### Leave Allocation
- Casual Leave: 12 days/year
- Sick Leave: 10 days/year
- Celebratory Leave: 3 days/year
- Earned Leave: 15 days/year

### Approval Workflow
- Review requests within 24 hours
- Check team availability
- Communicate with employee

### Year-end Process
- Reset balances for new year
- Archive old data
- Generate annual reports

## 🚀 Future Enhancements

- Email notifications
- Leave calendar view
- Carry forward unused leaves
- Half-day leave support
- Leave encashment
- Manager hierarchy
- Mobile app

## 📞 Support

For help:
1. Read **LEAVE_QUICK_START.md**
2. Check **LEAVE_MANAGEMENT_GUIDE.md**
3. Review SQL schema
4. Check Flask logs

## 📄 License

Part of Face Recognition Attendance System - MIT License

## 🎉 Status

✅ **Production Ready**  
✅ **Fully Tested**  
✅ **Well Documented**  
✅ **Easy to Use**

---

**Version:** 1.0  
**Last Updated:** December 2024  
**Developed by:** Amazon Q
