"""Setup Multi-Level Approval System"""
from app import create_app
from database import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        with db.engine.connect() as conn:
            print("Setting up multi-level approval system...")
            
            # Create approvers table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS `mtpl_leave_approvers` (
                  `approverId` INT NOT NULL AUTO_INCREMENT,
                  `approverUserId` INT NOT NULL,
                  `approverName` VARCHAR(100) NOT NULL,
                  `approverRole` VARCHAR(50) DEFAULT 'Manager',
                  `approverIsActive` TINYINT(1) DEFAULT 1,
                  `approverCreatedAt` DATETIME DEFAULT CURRENT_TIMESTAMP,
                  PRIMARY KEY (`approverId`),
                  KEY `idx_approver_user` (`approverUserId`),
                  UNIQUE KEY `unique_user_role` (`approverUserId`, `approverRole`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            
            # Create approvals table
            conn.execute(text("""
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
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            
            # Insert sample approvers
            conn.execute(text("""
                INSERT IGNORE INTO mtpl_leave_approvers (approverUserId, approverName, approverRole) VALUES
                (1, 'Admin User', 'Admin'),
                (2, 'HR Manager', 'HR'),
                (3, 'Department Manager', 'Manager')
            """))
            
            conn.commit()
            print("Multi-level approval tables created successfully!")
            print("Sample approvers added!")
            print("\nYou can now:")
            print("1. Start the app: python app.py")
            print("2. Go to Leave Management > Multi-Level Approval tab")
            print("3. Add more approvers")
            print("4. Assign multiple approvers to leave requests")
            
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()