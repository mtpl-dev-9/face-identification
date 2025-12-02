"""Verify complete leave system setup"""
from app import create_app
from database import db

app = create_app()

with app.app_context():
    try:
        with db.engine.connect() as conn:
            # Check users
            result = conn.execute(db.text("SELECT COUNT(*) FROM mtpl_users"))
            users_count = result.fetchone()[0]
            print(f"Users: {users_count}")
            
            # Check leave types
            result = conn.execute(db.text("SELECT COUNT(*) FROM mtpl_leave_types"))
            types_count = result.fetchone()[0]
            print(f"Leave Types: {types_count}")
            
            # Check allotments
            result = conn.execute(db.text("SELECT COUNT(*) FROM mtpl_leave_allotment"))
            allotments_count = result.fetchone()[0]
            print(f"Leave Allotments: {allotments_count}")
            
            # Show sample leave types
            if types_count > 0:
                print("\nLeave Types:")
                result = conn.execute(db.text("SELECT leaveTypeId, leaveTypeName FROM mtpl_leave_types LIMIT 5"))
                for row in result:
                    print(f"  {row[0]}: {row[1]}")
            
            # Show sample allotments
            if allotments_count > 0:
                print("\nSample Allotments:")
                result = conn.execute(db.text("""
                    SELECT a.allotmentUserId, a.allotmentTotal, a.allotmentYear, 
                           lt.leaveTypeName
                    FROM mtpl_leave_allotment a
                    JOIN mtpl_leave_types lt ON a.allotmentLeaveTypeId = lt.leaveTypeId
                    LIMIT 5
                """))
                for row in result:
                    print(f"  User {row[0]}: {row[1]} {row[3]} ({row[2]})")
                    
    except Exception as e:
        print(f"Error: {e}")