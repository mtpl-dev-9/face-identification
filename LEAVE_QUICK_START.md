# Leave Management - Quick Start Guide

## 🚀 Setup (One-Time)

### Step 1: Run SQL Schema
```bash
mysql -u root -p mtpl_website < leave_management_schema.sql
```

### Step 2: Initialize System
```bash
python init_leave_system.py
```

### Step 3: Start Application
```bash
python app.py
```

### Step 4: Access Leave Management
Open: **http://127.0.0.1:5000/leave-management**

---

## 👨‍💼 Admin Tasks

### Create Leave Types
1. Go to **Admin Panel** tab
2. Enter leave type name (e.g., "Casual Leave")
3. Click **Add**

**Common Leave Types:**
- Casual Leave
- Sick Leave
- Celebratory Leave
- Earned Leave
- Maternity Leave
- Paternity Leave

### Assign Leave Balance
1. Select **Employee**
2. Select **Leave Type**
3. Enter **Total Leaves** (e.g., 12)
4. Enter **Year** (e.g., 2024)
5. Click **Assign Balance**

**Recommended Allocation:**
- Casual Leave: 12 days/year
- Sick Leave: 10 days/year
- Celebratory Leave: 3 days/year
- Earned Leave: 15 days/year

### Approve/Reject Requests
1. Go to **Leave Requests** tab
2. Filter by **Pending**
3. Click ✅ to approve or ❌ to reject

---

## 👨‍💻 Employee Tasks

### Check Leave Balance
1. Go to **Employee Panel** tab
2. Select your name
3. View balance: Total | Used | Remaining

### Request Leave
1. Select your name
2. Select leave type
3. Choose from date and to date
4. Enter reason (optional)
5. Click **Submit Request**

**System will:**
- Calculate days automatically
- Check if balance is sufficient
- Create request with "pending" status

---

## 📊 API Examples

### Get Leave Types
```bash
curl http://127.0.0.1:5000/api/leave-types
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

---

## 🔍 Common Queries

### Check Employee Leave Balance
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
  AND u.userId = 1;
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

---

## ⚠️ Troubleshooting

### "Insufficient leave balance"
**Solution:** Admin needs to assign leave balance first

### Leave types not showing
**Solution:** Run `init_leave_system.py` or create manually

### Cannot approve request
**Solution:** Check if employee has sufficient balance

---

## 📋 Workflow Example

**Scenario:** Employee requests 3 days casual leave

1. **Employee:** Requests Dec 25-27 (3 days)
2. **System:** Validates balance (12 total, 2 used, 10 remaining ✅)
3. **System:** Creates request with status "pending"
4. **Admin:** Reviews and approves
5. **System:** Updates balance (used: 2 → 5, remaining: 10 → 7)
6. **System:** Marks request as "approved"

---

## 📞 Need Help?

Read full documentation: **LEAVE_MANAGEMENT_GUIDE.md**
