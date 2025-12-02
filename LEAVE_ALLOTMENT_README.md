# 🏖️ Leave Allotment System

> A complete leave allocation system using `mtpl_leave_allotment` database table

## ✨ Features

✅ **Database Storage** - All allocations in `mtpl_leave_allotment` table
✅ **Decimal Support** - Half-day leaves (0.5, 12.5, etc.)
✅ **Bulk Operations** - Assign to multiple users at once
✅ **Default Assignment** - One-click for all users
✅ **Year-wise Tracking** - Separate allocations per year
✅ **Audit Trail** - Tracks who assigned and when
✅ **RESTful API** - Complete CRUD operations
✅ **User-friendly UI** - Admin and Employee panels

## 🚀 Quick Start

### 1. Setup (One-time)

```bash
# Create database table
mysql -u admin -p mtpl_website < leave_allotment_schema.sql

# Initialize system
python init_leave_allotment.py

# Start application
python app.py
```

### 2. Assign Leaves

**Option A: Web Interface**
```
1. Open: http://127.0.0.1:5000/leave-management
2. Go to Admin Panel → Assign Default Leaves
3. Set: Casual: 4, Sick: 7, Celebratory: 0.5
4. Click: "Assign to All Users"
```

**Option B: API**
```bash
curl -X POST http://127.0.0.1:5000/api/leave-allotments/default \
  -H "Content-Type: application/json" \
  -d '{"year":2024,"defaults":{"casual":4,"sick":7,"celebratory":0.5},"assigned_by":1}'
```

### 3. View Balance

**Web Interface:**
```
1. Go to Employee Panel
2. Select employee
3. View balance
```

**Database:**
```sql
SELECT * FROM mtpl_leave_allotment WHERE allotmentUserId = 1;
```

## 📊 Database Structure

### Table: `mtpl_leave_allotment`

| Column | Type | Description |
|--------|------|-------------|
| `allotmentId` | INT | Primary key |
| `allotmentUserId` | INT | User ID |
| `allotmentLeaveTypeId` | INT | Leave type ID |
| `allotmentTotal` | DECIMAL(5,1) | Total leaves |
| `allotmentYear` | INT | Year |
| `allotmentAssignedBy` | INT | Who assigned |
| `allotmentAssignedAt` | DATETIME | When assigned |
| `allotmentUpdatedAt` | DATETIME | Last update |

### Example Data

```
┌────┬────────┬──────────┬───────┬──────┐
│ ID │ UserID │ LeaveType│ Total │ Year │
├────┼────────┼──────────┼───────┼──────┤
│ 1  │ 1      │ 1        │ 4.0   │ 2024 │ ← Casual Leave
│ 2  │ 1      │ 2        │ 7.0   │ 2024 │ ← Sick Leave
│ 3  │ 1      │ 3        │ 0.5   │ 2024 │ ← Celebratory Leave
└────┴────────┴──────────┴───────┴──────┘
```

## 🔌 API Endpoints

### Get Allotments
```http
GET /api/leave-allotments?user_id={id}&year={year}
```

### Create Allotment
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

### Bulk Assign
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

### Assign Default to All
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

### Delete Allotment
```http
DELETE /api/leave-allotments/{id}
```

## 🎨 UI Display

### Employee View

```
┌─────────────────────────────────┐
│ My Leave Balance                │
├─────────────────────────────────┤
│ Casual Leave                    │
│ Total: 4 | Used: 0 | Remaining: 4│
├─────────────────────────────────┤
│ Sick Leave                      │
│ Total: 7 | Used: 0 | Remaining: 7│
├─────────────────────────────────┤
│ Celebratory Leave               │
│ Total: 0.5 | Used: 0 | Remaining: 0.5│
└─────────────────────────────────┘
```

## 🧪 Testing

```bash
# Run test script
python test_leave_allotment.py

# Expected output:
# ✓ Leave Types: 3
# ✓ Leave Allotments: 9
# ✓ Active Users: 3
```

## 📚 Documentation

| File | Description |
|------|-------------|
| **[SUMMARY.md](SUMMARY.md)** | ⭐ Complete overview - START HERE |
| **[QUICK_START_LEAVE_ALLOTMENT.md](QUICK_START_LEAVE_ALLOTMENT.md)** | Quick reference guide |
| **[LEAVE_ALLOTMENT_GUIDE.md](LEAVE_ALLOTMENT_GUIDE.md)** | Complete detailed guide |
| **[LEAVE_ALLOTMENT_CHANGES.md](LEAVE_ALLOTMENT_CHANGES.md)** | What changed and why |
| **[LEAVE_ALLOTMENT_DIAGRAM.md](LEAVE_ALLOTMENT_DIAGRAM.md)** | Visual architecture |
| **[IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md)** | Step-by-step checklist |
| **[LEAVE_ALLOTMENT_INDEX.md](LEAVE_ALLOTMENT_INDEX.md)** | Documentation index |

## 💡 Usage Examples

### Example 1: Assign to Single User

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

### Example 2: Assign to Multiple Users

```bash
curl -X POST http://127.0.0.1:5000/api/leave-allotments/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "user_ids": [1, 2, 3],
    "leave_type_id": 1,
    "total": 4,
    "year": 2024,
    "assigned_by": 1
  }'
```

### Example 3: View User Balance

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

## 🔧 Configuration

### Database Connection

Update in `config.py`:
```python
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://admin:password@host:3306/mtpl_website"
```

### Leave Types

Default leave types:
- Casual Leave (4 days)
- Sick Leave (7 days)
- Celebratory Leave (0.5 days)

## 🚨 Troubleshooting

### Issue: No data showing

**Solution:**
```bash
# Check if table exists
mysql -u admin -p mtpl_website -e "SHOW TABLES LIKE 'mtpl_leave_allotment';"

# Check data count
mysql -u admin -p mtpl_website -e "SELECT COUNT(*) FROM mtpl_leave_allotment;"

# If empty, assign default leaves via web interface
```

### Issue: API not working

**Solution:**
```bash
# Check if app is running
curl http://127.0.0.1:5000/api/leave-types

# Verify database connection in config.py
```

## 📈 What You Can Do

✅ Assign leaves to any user
✅ Bulk assign to multiple users
✅ Assign default leaves to all users
✅ View employee balances
✅ Track who assigned and when
✅ Support decimal leaves (0.5)
✅ Manage year-wise allocations
✅ Use RESTful API
✅ Query database directly

## 🎯 Success Criteria

All of these should be true:

✅ Table `mtpl_leave_allotment` exists
✅ Table has data
✅ API endpoints return correct responses
✅ Frontend displays balances correctly
✅ Admin can assign leaves
✅ Employees can view balances
✅ No errors in logs

## 📞 Support

- **Complete Guide:** [LEAVE_ALLOTMENT_GUIDE.md](LEAVE_ALLOTMENT_GUIDE.md)
- **Quick Start:** [QUICK_START_LEAVE_ALLOTMENT.md](QUICK_START_LEAVE_ALLOTMENT.md)
- **Test Script:** `python test_leave_allotment.py`
- **API Docs:** http://127.0.0.1:5000/api/docs

## 🏆 Status

✅ **COMPLETE AND READY TO USE**

---

**Version:** 1.0  
**Last Updated:** 2024  
**License:** MIT

**Quick Links:**
- [📖 Complete Guide](LEAVE_ALLOTMENT_GUIDE.md)
- [🚀 Quick Start](QUICK_START_LEAVE_ALLOTMENT.md)
- [📋 Checklist](IMPLEMENTATION_CHECKLIST.md)
- [📊 Diagrams](LEAVE_ALLOTMENT_DIAGRAM.md)
- [📚 Index](LEAVE_ALLOTMENT_INDEX.md)
