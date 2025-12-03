# Leave Type Fields Update

## ✅ What Was Done

Updated the leave type creation form to include 4 new fields:
1. **Is Paid** - Whether the leave is paid or unpaid
2. **Encashable** - Whether unused leaves can be encashed
3. **Require Approval** - Whether leave requests need approval
4. **Require Attachment** - Whether attachments are required for leave requests

## 📊 Database Changes

### New Columns Added to `mtpl_leave_types`

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| `leaveTypeIsPaid` | TINYINT(1) | 1 | 1 = Paid, 0 = Unpaid |
| `leaveTypeIsEncashable` | TINYINT(1) | 0 | 1 = Encashable, 0 = Not encashable |
| `leaveTypeRequireApproval` | TINYINT(1) | 1 | 1 = Needs approval, 0 = Auto-approved |
| `leaveTypeRequireAttachment` | TINYINT(1) | 0 | 1 = Attachment required, 0 = Optional |

### Storage Format

- **Name**: VARCHAR (character string)
- **Other fields**: TINYINT(1) stored as 1 or 0 (boolean)

## 🚀 How to Update Database

### Option 1: Run SQL Script

```bash
mysql -u admin -p mtpl_website < update_leave_types_schema.sql
```

### Option 2: Manual SQL

```sql
ALTER TABLE `mtpl_leave_types` 
ADD COLUMN `leaveTypeIsPaid` TINYINT(1) DEFAULT 1 AFTER `leaveTypeName`,
ADD COLUMN `leaveTypeIsEncashable` TINYINT(1) DEFAULT 0 AFTER `leaveTypeIsPaid`,
ADD COLUMN `leaveTypeRequireApproval` TINYINT(1) DEFAULT 1 AFTER `leaveTypeIsEncashable`,
ADD COLUMN `leaveTypeRequireAttachment` TINYINT(1) DEFAULT 0 AFTER `leaveTypeRequireApproval`;
```

## 🎨 UI Changes

### Before
```
┌─────────────────────────────────┐
│ Manage Leave Types              │
├─────────────────────────────────┤
│ [Leave Type Name] [Add Button]  │
│                                 │
│ • Casual Leave     [Delete]     │
│ • Sick Leave       [Delete]     │
└─────────────────────────────────┘
```

### After
```
┌─────────────────────────────────┐
│ Manage Leave Types              │
├─────────────────────────────────┤
│ [Leave Type Name]               │
│ ☑ Is Paid        ☐ Encashable   │
│ ☑ Require Approval ☐ Attachment │
│ [Add Leave Type Button]         │
│                                 │
│ • Casual Leave                  │
│   [Paid] [Needs Approval]       │
│   [Delete]                      │
│                                 │
│ • Sick Leave                    │
│   [Paid] [Encashable]           │
│   [Needs Approval]              │
│   [Delete]                      │
└─────────────────────────────────┘
```

## 📝 Usage Example

### Create Leave Type via UI

1. Go to http://127.0.0.1:5000/leave-management
2. Admin Panel → Manage Leave Types
3. Enter name: "Casual Leave"
4. Check: ☑ Is Paid
5. Check: ☑ Require Approval
6. Uncheck: ☐ Encashable
7. Uncheck: ☐ Require Attachment
8. Click "Add Leave Type"

### Create Leave Type via API

```bash
curl -X POST http://127.0.0.1:5000/api/leave-types \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Casual Leave",
    "is_paid": true,
    "is_encashable": false,
    "require_approval": true,
    "require_attachment": false
  }'
```

### Response

```json
{
  "success": true,
  "leave_type": {
    "id": 1,
    "name": "Casual Leave",
    "is_paid": true,
    "is_encashable": false,
    "require_approval": true,
    "require_attachment": false,
    "is_active": true,
    "created_at": "2024-01-01T10:00:00Z"
  }
}
```

## 🗄️ Database Examples

### Example 1: Paid Casual Leave

```sql
INSERT INTO mtpl_leave_types 
(leaveTypeName, leaveTypeIsPaid, leaveTypeIsEncashable, leaveTypeRequireApproval, leaveTypeRequireAttachment)
VALUES 
('Casual Leave', 1, 0, 1, 0);
```

**Result:**
- Name: Casual Leave (VARCHAR)
- Is Paid: 1 (Yes)
- Encashable: 0 (No)
- Require Approval: 1 (Yes)
- Require Attachment: 0 (No)

### Example 2: Unpaid Leave

```sql
INSERT INTO mtpl_leave_types 
(leaveTypeName, leaveTypeIsPaid, leaveTypeIsEncashable, leaveTypeRequireApproval, leaveTypeRequireAttachment)
VALUES 
('Unpaid Leave', 0, 0, 1, 1);
```

**Result:**
- Name: Unpaid Leave (VARCHAR)
- Is Paid: 0 (No)
- Encashable: 0 (No)
- Require Approval: 1 (Yes)
- Require Attachment: 1 (Yes)

### Example 3: Encashable Sick Leave

```sql
INSERT INTO mtpl_leave_types 
(leaveTypeName, leaveTypeIsPaid, leaveTypeIsEncashable, leaveTypeRequireApproval, leaveTypeRequireAttachment)
VALUES 
('Sick Leave', 1, 1, 1, 1);
```

**Result:**
- Name: Sick Leave (VARCHAR)
- Is Paid: 1 (Yes)
- Encashable: 1 (Yes)
- Require Approval: 1 (Yes)
- Require Attachment: 1 (Yes - medical certificate)

## 📊 View Data

### Query All Leave Types

```sql
SELECT 
  leaveTypeId,
  leaveTypeName,
  CASE WHEN leaveTypeIsPaid = 1 THEN 'Paid' ELSE 'Unpaid' END AS paid_status,
  CASE WHEN leaveTypeIsEncashable = 1 THEN 'Yes' ELSE 'No' END AS encashable,
  CASE WHEN leaveTypeRequireApproval = 1 THEN 'Yes' ELSE 'No' END AS needs_approval,
  CASE WHEN leaveTypeRequireAttachment = 1 THEN 'Yes' ELSE 'No' END AS needs_attachment
FROM mtpl_leave_types
WHERE leaveTypeIsActive = 1;
```

### Example Output

```
┌────┬───────────────┬─────────┬────────────┬────────────────┬──────────────────┐
│ ID │ Name          │ Paid    │ Encashable │ Needs Approval │ Needs Attachment │
├────┼───────────────┼─────────┼────────────┼────────────────┼──────────────────┤
│ 1  │ Casual Leave  │ Paid    │ No         │ Yes            │ No               │
│ 2  │ Sick Leave    │ Paid    │ Yes        │ Yes            │ Yes              │
│ 3  │ Unpaid Leave  │ Unpaid  │ No         │ Yes            │ Yes              │
└────┴───────────────┴─────────┴────────────┴────────────────┴──────────────────┘
```

## 🔧 Updated Files

1. **models.py** - Added 4 new columns to LeaveType model
2. **app.py** - Updated API endpoint to accept new fields
3. **templates/leave_management.html** - Updated form and display
4. **update_leave_types_schema.sql** - SQL migration script

## ✅ Testing

### Test 1: Create Leave Type with All Fields

```bash
curl -X POST http://127.0.0.1:5000/api/leave-types \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Leave",
    "is_paid": true,
    "is_encashable": true,
    "require_approval": true,
    "require_attachment": true
  }'
```

### Test 2: Verify in Database

```sql
SELECT * FROM mtpl_leave_types WHERE leaveTypeName = 'Test Leave';
```

**Expected:**
- leaveTypeName: "Test Leave"
- leaveTypeIsPaid: 1
- leaveTypeIsEncashable: 1
- leaveTypeRequireApproval: 1
- leaveTypeRequireAttachment: 1

### Test 3: View in UI

1. Go to http://127.0.0.1:5000/leave-management
2. Check "Manage Leave Types" section
3. Should see badges: [Paid] [Encashable] [Needs Approval] [Needs Attachment]

## 🎯 Summary

### What Changed

✅ **Database**: 4 new TINYINT(1) columns added
✅ **API**: Accepts 4 new boolean fields
✅ **UI**: Form with 4 checkboxes
✅ **Display**: Shows badges for each property

### Storage Format

- **Name**: Character string (VARCHAR)
- **Flags**: 1 or 0 (TINYINT stored as boolean)

### Default Values

- Is Paid: ✅ Yes (1)
- Encashable: ❌ No (0)
- Require Approval: ✅ Yes (1)
- Require Attachment: ❌ No (0)

---

**Status:** ✅ COMPLETE
**Version:** 1.0
**Date:** 2024
