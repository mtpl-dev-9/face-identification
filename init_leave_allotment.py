"""
Initialize Leave Allotment System
This script creates the leave allotment table and sets up default leave types
"""

from app import create_app
from database import db
from models import LeaveType, LeaveAllotment, User
from datetime import datetime
import pytz

IST = pytz.timezone('Asia/Kolkata')

def init_leave_allotment_system():
    app = create_app()
    
    with app.app_context():
        print("Initializing Leave Allotment System...")
        
        # Create all tables
        db.create_all()
        print("✓ Database tables created")
        
        # Create default leave types if they don't exist
        leave_types_data = [
            'Casual Leave',
            'Sick Leave',
            'Celebratory Leave'
        ]
        
        created_types = []
        for leave_name in leave_types_data:
            existing = LeaveType.query.filter_by(leaveTypeName=leave_name).first()
            if not existing:
                leave_type = LeaveType(leaveTypeName=leave_name)
                db.session.add(leave_type)
                created_types.append(leave_name)
        
        db.session.commit()
        
        if created_types:
            print(f"✓ Created leave types: {', '.join(created_types)}")
        else:
            print("✓ Leave types already exist")
        
        # Count existing allotments
        allotment_count = LeaveAllotment.query.count()
        user_count = User.query.filter_by(userIsActive='1').count()
        
        print(f"✓ Found {user_count} active users")
        print(f"✓ Found {allotment_count} existing leave allotments")
        
        print("\n" + "="*50)
        print("Leave Allotment System initialized successfully!")
        print("="*50)
        print("\nNext steps:")
        print("1. Go to http://127.0.0.1:5000/leave-management")
        print("2. Use 'Assign Default Leaves' to assign leaves to all users")
        print("3. Or use 'Assign Leave Balance' to assign individually")
        print("4. Check the database table 'mtpl_leave_allotment' for records")

if __name__ == '__main__':
    init_leave_allotment_system()
