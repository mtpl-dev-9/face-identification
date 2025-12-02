"""Insert a test record you can verify in Workbench"""
from app import create_app
from database import db
from models import LeaveAllotment
from datetime import datetime

app = create_app()

with app.app_context():
    try:
        # Insert a test record with current timestamp
        now = datetime.now()
        test_allotment = LeaveAllotment(
            allotmentUserId=999,
            allotmentLeaveTypeId=1,
            allotmentTotal=99.5,
            allotmentYear=2024,
            allotmentAssignedBy=1
        )
        
        db.session.add(test_allotment)
        db.session.commit()
        
        print("Test record inserted!")
        print(f"User ID: 999")
        print(f"Total: 99.5")
        print(f"Year: 2024")
        print(f"Time: {now}")
        print("\nNow check in MySQL Workbench:")
        print("SELECT * FROM mtpl_leave_allotment WHERE allotmentUserId = 999;")
        
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()