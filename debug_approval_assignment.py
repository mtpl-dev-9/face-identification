"""Debug approval assignment"""
from app import create_app
from database import db
from multilevel_models import LeaveApproval
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        with db.engine.connect() as conn:
            # Check if approvals table exists
            result = conn.execute(text("SHOW TABLES LIKE 'mtpl_leave_approvals'"))
            if result.fetchone():
                print("Table mtpl_leave_approvals exists")
                
                # Check table structure
                result = conn.execute(text("DESCRIBE mtpl_leave_approvals"))
                print("\nTable structure:")
                for row in result:
                    print(f"  {row[0]} - {row[1]}")
                
                # Check existing data
                result = conn.execute(text("SELECT COUNT(*) FROM mtpl_leave_approvals"))
                count = result.fetchone()[0]
                print(f"\nExisting approvals: {count}")
                
                if count > 0:
                    result = conn.execute(text("SELECT * FROM mtpl_leave_approvals LIMIT 5"))
                    print("\nSample data:")
                    for row in result:
                        print(f"  {row}")
                        
                # Test inserting multiple approvals for same request
                print("\nTesting multiple approvals for request ID 1...")
                try:
                    conn.execute(text("""
                        INSERT INTO mtpl_leave_approvals 
                        (approvalLeaveRequestId, approvalApproverId) 
                        VALUES (999, 1), (999, 2), (999, 3)
                    """))
                    conn.commit()
                    print("Successfully inserted multiple approvals!")
                    
                    # Check the inserted data
                    result = conn.execute(text("SELECT * FROM mtpl_leave_approvals WHERE approvalLeaveRequestId = 999"))
                    print("Inserted approvals:")
                    for row in result:
                        print(f"  Request: {row[1]}, Approver: {row[2]}, Status: {row[3]}")
                        
                    # Clean up test data
                    conn.execute(text("DELETE FROM mtpl_leave_approvals WHERE approvalLeaveRequestId = 999"))
                    conn.commit()
                    print("Test data cleaned up")
                    
                except Exception as e:
                    print(f"Error inserting multiple approvals: {e}")
                    
            else:
                print("mtpl_leave_approvals table does not exist!")
                print("Run: python setup_multilevel_approval.py")
                
    except Exception as e:
        print(f"Error: {e}")