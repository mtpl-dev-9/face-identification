"""Debug database insert and check if data is committed"""
from app import create_app
from database import db

app = create_app()

with app.app_context():
    try:
        with db.engine.connect() as conn:
            # Check current data
            result = conn.execute(db.text("SELECT COUNT(*) FROM mtpl_leave_allotment"))
            count_before = result.fetchone()[0]
            print(f"Records before: {count_before}")
            
            # Insert test record with explicit commit
            conn.execute(db.text("""
                INSERT INTO mtpl_leave_allotment 
                (allotmentUserId, allotmentLeaveTypeId, allotmentTotal, allotmentYear, allotmentAssignedBy)
                VALUES (999, 1, 5.0, 2024, 1)
            """))
            conn.commit()
            
            # Check after insert
            result = conn.execute(db.text("SELECT COUNT(*) FROM mtpl_leave_allotment"))
            count_after = result.fetchone()[0]
            print(f"Records after: {count_after}")
            
            # Show the new record
            result = conn.execute(db.text("SELECT * FROM mtpl_leave_allotment WHERE allotmentUserId = 999"))
            for row in result:
                print(f"New record: {row}")
                
    except Exception as e:
        print(f"Error: {e}")