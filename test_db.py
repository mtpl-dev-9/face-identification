from app import app
from models import LeaveAllotment
from database import db

with app.app_context():
    # Test insert
    print("Testing database connection...")
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Create test allotment
    test = LeaveAllotment(
        allotmentUserId=1,
        allotmentLeaveTypeId=1,
        allotmentTotal=10.0,
        allotmentYear=2025,
        allotmentAssignedBy=1
    )
    
    db.session.add(test)
    db.session.commit()
    
    print(f"Inserted allotment with ID: {test.allotmentId}")
    
    # Query back
    count = LeaveAllotment.query.count()
    print(f"Total allotments in database: {count}")
    
    all_allotments = LeaveAllotment.query.all()
    for a in all_allotments:
        print(f"  ID: {a.allotmentId}, User: {a.allotmentUserId}, Total: {a.allotmentTotal}")
