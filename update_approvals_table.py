"""Add user ID to leave approvals table"""
from app import create_app
from database import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        with db.engine.connect() as conn:
            print("Adding user ID to leave approvals table...")
            
            # Add user ID column
            try:
                conn.execute(text("ALTER TABLE `mtpl_leave_approvals` ADD COLUMN `approvalUserId` INT NULL AFTER `approvalApproverId`"))
                print("Column added successfully!")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print("Column already exists!")
                else:
                    print(f"Error adding column: {e}")
            
            # Update existing records
            conn.execute(text("""
                UPDATE mtpl_leave_approvals la
                JOIN mtpl_leave_requests lr ON la.approvalLeaveRequestId = lr.leaveRequestId
                SET la.approvalUserId = lr.leaveRequestUserId
            """))
            
            conn.commit()
            print("Existing records updated with user IDs!")
            
            # Show sample data
            result = conn.execute(text("""
                SELECT la.approvalId, la.approvalLeaveRequestId, la.approvalUserId, 
                       la.approvalApproverId, la.approvalStatus
                FROM mtpl_leave_approvals la
                LIMIT 5
            """))
            
            print("\nSample approval records:")
            for row in result:
                print(f"  Approval ID: {row[0]}, Request: {row[1]}, User: {row[2]}, Approver: {row[3]}, Status: {row[4]}")
                
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()