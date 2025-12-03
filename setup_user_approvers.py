"""Setup User Approvers System"""
from app import create_app
from database import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        with db.engine.connect() as conn:
            print("Setting up user approvers system...")
            
            # Create user approvers table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS `mtpl_user_approvers` (
                  `userApproverId` INT NOT NULL AUTO_INCREMENT,
                  `userApproverUserId` INT NOT NULL,
                  `userApproverApproverId` INT NOT NULL,
                  `userApproverIsActive` TINYINT(1) DEFAULT 1,
                  `userApproverCreatedAt` DATETIME DEFAULT CURRENT_TIMESTAMP,
                  PRIMARY KEY (`userApproverId`),
                  KEY `idx_user` (`userApproverUserId`),
                  KEY `idx_approver` (`userApproverApproverId`),
                  UNIQUE KEY `unique_user_approver` (`userApproverUserId`, `userApproverApproverId`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            
            # Insert sample assignments
            conn.execute(text("""
                INSERT IGNORE INTO mtpl_user_approvers (userApproverUserId, userApproverApproverId) VALUES
                (1, 8), (1, 9), (1, 10),
                (4, 8), (4, 9),
                (5, 9), (5, 10)
            """))
            
            conn.commit()
            print("User approvers system created successfully!")
            
            # Show current assignments
            result = conn.execute(text("""
                SELECT ua.userApproverUserId, ua.userApproverApproverId, 
                       la.approverName, la.approverRole
                FROM mtpl_user_approvers ua
                JOIN mtpl_leave_approvers la ON ua.userApproverApproverId = la.approverId
            """))
            
            print("\nCurrent user-approver assignments:")
            for row in result:
                print(f"  User {row[0]} -> {row[2]} ({row[3]})")
                
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()