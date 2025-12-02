"""Test database insert with explicit commit"""
from app import create_app
from database import db
from models import LeaveAllotment

app = create_app()

with app.app_context():
    try:
        print("Before insert:")
        count_before = LeaveAllotment.query.count()
        print(f"Count: {count_before}")
        
        # Insert test record
        test_allotment = LeaveAllotment(
            allotmentUserId=888,
            allotmentLeaveTypeId=1,
            allotmentTotal=10.0,
            allotmentYear=2024,
            allotmentAssignedBy=1
        )
        
        db.session.add(test_allotment)
        print("Added to session")
        
        db.session.commit()
        print("Committed to database")
        
        # Check count after
        count_after = LeaveAllotment.query.count()
        print(f"Count after: {count_after}")
        
        # Verify the record exists
        test_record = LeaveAllotment.query.filter_by(allotmentUserId=888).first()
        if test_record:
            print(f"Record found: ID={test_record.allotmentId}, Total={test_record.allotmentTotal}")
        else:
            print("Record NOT found!")
            
        # Clean up
        if test_record:
            db.session.delete(test_record)
            db.session.commit()
            print("Test record deleted")
            
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()