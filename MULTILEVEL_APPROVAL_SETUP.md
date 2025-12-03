# Multi-Level Approval System Setup

## 1. Create Database Tables

Run this SQL in MySQL Workbench:

```sql
-- Run the schema
SOURCE multilevel_approval_schema.sql;
```

Or manually:

```sql
-- Table to store who can approve leave requests
CREATE TABLE IF NOT EXISTS `mtpl_leave_approvers` (
  `approverId` INT NOT NULL AUTO_INCREMENT,
  `approverUserId` INT NOT NULL,
  `approverName` VARCHAR(100) NOT NULL,
  `approverRole` VARCHAR(50) DEFAULT 'Manager',
  `approverIsActive` TINYINT(1) DEFAULT 1,
  `approverCreatedAt` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`approverId`),
  KEY `idx_approver_user` (`approverUserId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table to store approval workflow for each leave request
CREATE TABLE IF NOT EXISTS `mtpl_leave_approvals` (
  `approvalId` INT NOT NULL AUTO_INCREMENT,
  `approvalLeaveRequestId` INT NOT NULL,
  `approvalApproverId` INT NOT NULL,
  `approvalStatus` ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
  `approvalComments` TEXT,
  `approvalApprovedAt` DATETIME NULL,
  `approvalCreatedAt` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`approvalId`),
  KEY `idx_leave_request` (`approvalLeaveRequestId`),
  KEY `idx_approver` (`approvalApproverId`),
  UNIQUE KEY `unique_request_approver` (`approvalLeaveRequestId`, `approvalApproverId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert sample approvers
INSERT INTO mtpl_leave_approvers (approverUserId, approverName, approverRole) VALUES
(1, 'Admin User', 'Admin'),
(2, 'HR Manager', 'HR'),
(3, 'Department Manager', 'Manager');
```

## 2. How It Works

### Step 1: Admin Sets Up Approvers
```bash
POST /api/leave-approvers
{
  "user_id": 1,
  "name": "John Manager",
  "role": "Manager"
}
```

### Step 2: Employee Submits Leave Request
```bash
POST /api/leave-requests
{
  "user_id": 5,
  "leave_type_id": 1,
  "from_date": "2024-12-10",
  "to_date": "2024-12-12",
  "reason": "Family function"
}
```

### Step 3: Admin Assigns Multiple Approvers
```bash
POST /api/leave-requests/1/assign-approvers
{
  "approver_ids": [1, 2, 3]  // Admin, HR, Manager
}
```

### Step 4: Each Approver Approves/Rejects
```bash
POST /api/leave-approvals/1/approve
{
  "comments": "Approved by HR"
}

POST /api/leave-approvals/2/approve
{
  "comments": "Approved by Manager"
}

POST /api/leave-approvals/3/approve
{
  "comments": "Final approval by Admin"
}
```

### Step 5: Check Status
```bash
GET /api/leave-requests/1/approvals
```

**Response:**
```json
{
  "success": true,
  "approvals": [...],
  "summary": {
    "total": 3,
    "approved": 3,
    "rejected": 0,
    "pending": 0,
    "overall_status": "fully_approved"
  }
}
```

## 3. API Endpoints

### Approver Management
- `GET /api/leave-approvers` - Get all approvers
- `POST /api/leave-approvers` - Add new approver
- `DELETE /api/leave-approvers/{id}` - Remove approver

### Multi-Level Approval
- `POST /api/leave-requests/{id}/assign-approvers` - Assign approvers to request
- `GET /api/leave-requests/{id}/approvals` - Get approval status
- `POST /api/leave-approvals/{id}/approve` - Individual approve
- `POST /api/leave-approvals/{id}/reject` - Individual reject
- `GET /api/my-pending-approvals/{user_id}` - Get my pending approvals

## 4. Approval Logic

1. **Admin assigns multiple approvers** to each leave request
2. **All approvers must approve** for final approval
3. **Any approver can reject** → Entire request rejected
4. **Approvers can approve in any order** (not level-based)
5. **Only when ALL approve** → Request is fully approved

## 5. Status Flow

```
Leave Request Created
        ↓
Admin Assigns Approvers (Admin, HR, Manager)
        ↓
Approvers Review (any order):
  - HR: Approved ✓
  - Manager: Approved ✓  
  - Admin: Pending...
        ↓
Admin Approves → FULLY APPROVED ✓
```

## 6. Test the System

```bash
# 1. Start app
python app.py

# 2. Add approvers via API or web interface
# 3. Create leave request
# 4. Assign multiple approvers
# 5. Each approver approves
# 6. Check final status
```

## 7. Web Interface Integration

Add this to your leave management template to show approval workflow and allow approvers to approve/reject requests.

The system is now ready for multi-level approval workflow!