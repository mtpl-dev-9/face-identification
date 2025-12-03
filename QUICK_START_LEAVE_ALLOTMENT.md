# Quick Start: Leave Allotment System

## 🚀 Setup (One-time)

```bash
# 1. Create table
mysql -u admin -p mtpl_website < leave_allotment_schema.sql

# 2. Initialize system
python init_leave_allotment.py

# 3. Start app
python app.py
```

## 📋 Usage

### Web Interface

**URL:** http://127.0.0.1:5000/leave-management

**Assign to Single User:**
1. Admin Panel → Assign Leave Balance
2. Select Employee
3. Select Leave Type
4. Enter Total (e.g., 4, 0.5, 12.5)
5. Click "Assign Balance"

**Assign to All Users:**
1. Admin Panel → Assign Default Leaves
2. Set Casual: 4, Sick: 7, Celebratory: 0.5
3. Click "Assign to All Users"

**View Balance:**
1. Employee Panel
2. Select Employee
3. See leave balance

### API Endpoints

**Get Allotments:**
```bash
curl http://127.0.0.1:5000/api/leave-allotments?user_id=1&year=2024
```

**Assign Leave:**
```bash
curl -X POST http://127.0.0.1:5000/api/leave-allotments \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"leave_type_id":1,"total":4,"year":2024,"assigned_by":1}'
```

**Bulk Assign:**
```bash
curl -X POST http://127.0.0.1:5000/api/leave-allotments/bulk \
  -H "Content-Type: application/json" \
  -d '{"user_ids":[1,2,3],"leave_type_id":1,"total":4,"year":2024,"assigned_by":1}'
```

**Default Assign:**
```bash
curl -X POST http://127.0.0.1:5000/api/leave-allotments/default \
  -H "Content-Type: application/json" \
  -d '{"year":2024,"defaults":{"casual":4,"sick":7,"celebratory":0.5},"assigned_by":1}'
```

## 🗄️ Database

**Table:** `mtpl_leave_allotment`

**View Data:**
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
ORDER BY u.userFirstName;
```

**Count Records:**
```sql
SELECT COUNT(*) FROM mtpl_leave_allotment;
```

**User's Balance:**
```sql
SELECT * FROM mtpl_leave_allotment 
WHERE allotmentUserId = 1 AND allotmentYear = 2024;
```

## ✅ Test

```bash
python test_leave_allotment.py
```

## 📚 Documentation

- **Complete Guide:** `LEAVE_ALLOTMENT_GUIDE.md`
- **Changes Summary:** `LEAVE_ALLOTMENT_CHANGES.md`
- **SQL Schema:** `leave_allotment_schema.sql`
- **API Docs:** http://127.0.0.1:5000/api/docs

## 🔧 Troubleshooting

**No data showing?**
```bash
# Check table exists
mysql -u admin -p mtpl_website -e "SHOW TABLES LIKE 'mtpl_leave_allotment';"

# Check data
mysql -u admin -p mtpl_website -e "SELECT COUNT(*) FROM mtpl_leave_allotment;"

# Assign default leaves via web interface
```

**API not working?**
```bash
# Check app is running
curl http://127.0.0.1:5000/api/leave-types

# Check database connection in config.py
```

## 💡 Tips

- **Decimal Support:** Use 0.5 for half-day leaves
- **Bulk Operations:** Select multiple users with Ctrl+Click
- **Year-wise:** Separate allocations for each year
- **Audit Trail:** System tracks who assigned and when
- **Update vs Create:** System automatically updates existing records

## 📞 Support

- Check logs in terminal
- Review `LEAVE_ALLOTMENT_GUIDE.md`
- Test with `test_leave_allotment.py`
- Verify database with SQL queries above
