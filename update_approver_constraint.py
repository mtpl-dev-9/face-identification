"""Update approver table to allow multiple roles per user"""
from app import create_app
from database import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        with db.engine.connect() as conn:
            print("Updating approver table constraint...")
            
            # Add unique constraint on user+role combination
            try:
                conn.execute(text("""
                    ALTER TABLE mtpl_leave_approvers 
                    ADD UNIQUE KEY `unique_user_role` (`approverUserId`, `approverRole`)
                """))
                conn.commit()
                print("Constraint added successfully!")
            except Exception as e:
                if "Duplicate key name" in str(e):
                    print("Constraint already exists!")
                else:
                    print(f"Error adding constraint: {e}")
            
            # Now you can add same user with different roles
            print("\nTesting: Adding same user with different roles...")
            try:
                conn.execute(text("""
                    INSERT IGNORE INTO mtpl_leave_approvers (approverUserId, approverName, approverRole) VALUES
                    (1, 'Admin User', 'Admin'),
                    (1, 'Admin User', 'HR'),
                    (1, 'Admin User', 'Manager'),
                    (2, 'User 2', 'HR'),
                    (2, 'User 2', 'Manager')
                """))
                conn.commit()
                print("Sample multi-role approvers added!")
                
                # Show current approvers
                result = conn.execute(text("SELECT * FROM mtpl_leave_approvers"))
                print("\nCurrent approvers:")
                for row in result:
                    print(f"  ID: {row[0]}, User: {row[1]} ({row[2]}), Role: {row[3]}")
                    
            except Exception as e:
                print(f"Error adding sample data: {e}")
                
    except Exception as e:
        print(f"Error: {e}")