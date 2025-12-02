# Leave Allotment System - Implementation Checklist

## ✅ Pre-Implementation

- [ ] Backup current database
  ```bash
  mysqldump -u admin -p mtpl_website > backup_$(date +%Y%m%d).sql
  ```

- [ ] Verify Python dependencies installed
  ```bash
  pip list | grep -E "flask|sqlalchemy|pymysql"
  ```

- [ ] Check database connection in `config.py`
  ```python
  SQLALCHEMY_DATABASE_URI = "mysql+pymysql://admin:password@host:3306/mtpl_website"
  ```

## ✅ Database Setup

- [ ] Create `mtpl_leave_allotment` table
  ```bash
  mysql -u admin -p mtpl_website < leave_allotment_schema.sql
  ```

- [ ] Verify table created
  ```sql
  SHOW TABLES LIKE 'mtpl_leave_allotment';
  DESCRIBE mtpl_leave_allotment;
  ```

- [ ] Check foreign key constraints
  ```sql
  SHOW CREATE TABLE mtpl_leave_allotment;
  ```

## ✅ Code Deployment

- [ ] Updated files in place:
  - [x] `app.py` - New API endpoints added
  - [x] `templates/leave_management.html` - Frontend updated
  - [x] `models.py` - LeaveAllotment model exists
  - [x] `README.md` - Documentation updated

- [ ] New files created:
  - [x] `leave_allotment_schema.sql`
  - [x] `init_leave_allotment.py`
  - [x] `test_leave_allotment.py`
  - [x] `LEAVE_ALLOTMENT_GUIDE.md`
  - [x] `LEAVE_ALLOTMENT_CHANGES.md`
  - [x] `QUICK_START_LEAVE_ALLOTMENT.md`
  - [x] `LEAVE_ALLOTMENT_DIAGRAM.md`
  - [x] `IMPLEMENTATION_CHECKLIST.md`

## ✅ Initialization

- [ ] Run initialization script
  ```bash
  python init_leave_allotment.py
  ```

- [ ] Verify leave types created
  ```sql
  SELECT * FROM mtpl_leave_types;
  ```
  Expected: Casual Leave, Sick Leave, Celebratory Leave

- [ ] Check active users count
  ```sql
  SELECT COUNT(*) FROM mtpl_users WHERE userIsActive = '1';
  ```

## ✅ Testing

- [ ] Run test script
  ```bash
  python test_leave_allotment.py
  ```

- [ ] Start application
  ```bash
  python app.py
  ```

- [ ] Access leave management page
  ```
  http://127.0.0.1:5000/leave-management
  ```

- [ ] Test API endpoints:

  **Get Leave Types:**
  ```bash
  curl http://127.0.0.1:5000/api/leave-types
  ```

  **Get Allotments (should be empty initially):**
  ```bash
  curl http://127.0.0.1:5000/api/leave-allotments?user_id=1&year=2024
  ```

## ✅ Functional Testing

### Test 1: Assign Leave to Single User

- [ ] Go to Admin Panel → Assign Leave Balance
- [ ] Select a user
- [ ] Select "Casual Leave"
- [ ] Enter 4
- [ ] Enter current year
- [ ] Click "Assign Balance"
- [ ] Verify success message
- [ ] Check database:
  ```sql
  SELECT * FROM mtpl_leave_allotment WHERE allotmentUserId = 1;
  ```

### Test 2: View Employee Balance

- [ ] Go to Employee Panel
- [ ] Select the same user
- [ ] Verify balance shows:
  ```
  Casual Leave
  Total: 4 | Used: 0 | Remaining: 4
  ```

### Test 3: Bulk Assign

- [ ] Go to Admin Panel → Bulk Assign Leave Balance
- [ ] Select multiple users (Ctrl+Click)
- [ ] Select "Sick Leave"
- [ ] Enter 7
- [ ] Click "Assign"
- [ ] Verify success message with count
- [ ] Check database:
  ```sql
  SELECT COUNT(*) FROM mtpl_leave_allotment WHERE allotmentLeaveTypeId = 2;
  ```

### Test 4: Assign Default Leaves

- [ ] Go to Admin Panel → Assign Default Leaves
- [ ] Set Casual: 4, Sick: 7, Celebratory: 0.5
- [ ] Enter current year
- [ ] Click "Assign to All Users"
- [ ] Verify success message
- [ ] Check database:
  ```sql
  SELECT 
    allotmentYear,
    COUNT(*) as total_records,
    COUNT(DISTINCT allotmentUserId) as unique_users
  FROM mtpl_leave_allotment
  GROUP BY allotmentYear;
  ```
  Expected: 3 records per user

### Test 5: API Testing

- [ ] Test GET endpoint:
  ```bash
  curl http://127.0.0.1:5000/api/leave-allotments?user_id=1&year=2024
  ```

- [ ] Test POST endpoint:
  ```bash
  curl -X POST http://127.0.0.1:5000/api/leave-allotments \
    -H "Content-Type: application/json" \
    -d '{"user_id":1,"leave_type_id":1,"total":4,"year":2024,"assigned_by":1}'
  ```

- [ ] Test Bulk POST:
  ```bash
  curl -X POST http://127.0.0.1:5000/api/leave-allotments/bulk \
    -H "Content-Type: application/json" \
    -d '{"user_ids":[1,2],"leave_type_id":1,"total":4,"year":2024,"assigned_by":1}'
  ```

- [ ] Test Default POST:
  ```bash
  curl -X POST http://127.0.0.1:5000/api/leave-allotments/default \
    -H "Content-Type: application/json" \
    -d '{"year":2024,"defaults":{"casual":4,"sick":7,"celebratory":0.5},"assigned_by":1}'
  ```

## ✅ Data Verification

- [ ] Check total allotments:
  ```sql
  SELECT COUNT(*) FROM mtpl_leave_allotment;
  ```

- [ ] Check allotments per user:
  ```sql
  SELECT 
    allotmentUserId,
    COUNT(*) as leave_types_assigned
  FROM mtpl_leave_allotment
  WHERE allotmentYear = 2024
  GROUP BY allotmentUserId;
  ```

- [ ] View sample data:
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
  LIMIT 10;
  ```

- [ ] Check for duplicates (should be none):
  ```sql
  SELECT 
    allotmentUserId,
    allotmentLeaveTypeId,
    allotmentYear,
    COUNT(*) as count
  FROM mtpl_leave_allotment
  GROUP BY allotmentUserId, allotmentLeaveTypeId, allotmentYear
  HAVING count > 1;
  ```

## ✅ Edge Cases Testing

- [ ] Test decimal values (0.5, 12.5)
- [ ] Test update existing allotment
- [ ] Test with inactive users
- [ ] Test with non-existent user_id
- [ ] Test with invalid leave_type_id
- [ ] Test with past year
- [ ] Test with future year

## ✅ Performance Testing

- [ ] Test with 100+ users
- [ ] Test bulk assign to all users
- [ ] Check query performance:
  ```sql
  EXPLAIN SELECT * FROM mtpl_leave_allotment 
  WHERE allotmentUserId = 1 AND allotmentYear = 2024;
  ```

- [ ] Verify indexes exist:
  ```sql
  SHOW INDEX FROM mtpl_leave_allotment;
  ```

## ✅ Documentation Review

- [ ] Read `LEAVE_ALLOTMENT_GUIDE.md`
- [ ] Review `LEAVE_ALLOTMENT_CHANGES.md`
- [ ] Check `QUICK_START_LEAVE_ALLOTMENT.md`
- [ ] View `LEAVE_ALLOTMENT_DIAGRAM.md`
- [ ] Verify `README.md` updated

## ✅ User Acceptance Testing

- [ ] Admin can assign leaves
- [ ] Admin can bulk assign leaves
- [ ] Admin can assign default leaves
- [ ] Employee can view balance
- [ ] Balance displays correctly
- [ ] Data persists in database
- [ ] UI is responsive
- [ ] No errors in console

## ✅ Production Readiness

- [ ] Database backup completed
- [ ] All tests passed
- [ ] Documentation complete
- [ ] API endpoints working
- [ ] Frontend functional
- [ ] No console errors
- [ ] Performance acceptable
- [ ] Security reviewed

## ✅ Deployment

- [ ] Deploy to production server
- [ ] Run initialization on production
- [ ] Verify production database connection
- [ ] Test production endpoints
- [ ] Monitor logs for errors
- [ ] Inform users of new feature

## ✅ Post-Deployment

- [ ] Monitor application logs
- [ ] Check database growth
- [ ] Gather user feedback
- [ ] Document any issues
- [ ] Plan for improvements

## 🎯 Success Criteria

All of the following should be true:

✅ Table `mtpl_leave_allotment` exists and has data
✅ API endpoints return correct responses
✅ Frontend displays leave balances correctly
✅ Admin can assign leaves successfully
✅ Employees can view their balances
✅ Data persists correctly in database
✅ No errors in application logs
✅ Documentation is complete and accurate

## 📊 Metrics to Track

- Total allotments created
- Number of users with allotments
- Average allotments per user
- API response times
- Database query performance
- User adoption rate

## 🔍 Monitoring Queries

**Daily Check:**
```sql
-- Total allotments
SELECT COUNT(*) FROM mtpl_leave_allotment;

-- Users with allotments
SELECT COUNT(DISTINCT allotmentUserId) FROM mtpl_leave_allotment;

-- Recent assignments
SELECT * FROM mtpl_leave_allotment 
ORDER BY allotmentAssignedAt DESC 
LIMIT 10;
```

**Weekly Check:**
```sql
-- Allotments by year
SELECT allotmentYear, COUNT(*) 
FROM mtpl_leave_allotment 
GROUP BY allotmentYear;

-- Allotments by leave type
SELECT lt.leaveTypeName, COUNT(*) 
FROM mtpl_leave_allotment a
JOIN mtpl_leave_types lt ON a.allotmentLeaveTypeId = lt.leaveTypeId
GROUP BY lt.leaveTypeName;
```

## 📝 Notes

- Keep this checklist for future reference
- Update as needed based on experience
- Share with team members
- Use for training new developers

---

**Checklist Version:** 1.0
**Last Updated:** 2024
**Status:** Ready for Implementation
