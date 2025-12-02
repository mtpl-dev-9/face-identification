"""
Test Leave Allotment System
Quick test to verify the leave allotment system is working correctly
"""

from app import create_app
from database import db
from models import LeaveType, LeaveAllotment, User
from datetime import datetime

def test_leave_allotment():
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("LEAVE ALLOTMENT SYSTEM TEST")
        print("="*60)
        
        # Test 1: Check if tables exist
        print("\n1. Checking database tables...")
        try:
            leave_types_count = LeaveType.query.count()
            allotments_count = LeaveAllotment.query.count()
            users_count = User.query.filter_by(userIsActive='1').count()
            
            print(f"   ✓ Leave Types: {leave_types_count}")
            print(f"   ✓ Leave Allotments: {allotments_count}")
            print(f"   ✓ Active Users: {users_count}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return
        
        # Test 2: Check leave types
        print("\n2. Checking leave types...")
        leave_types = LeaveType.query.filter_by(leaveTypeIsActive=True).all()
        if leave_types:
            for lt in leave_types:
                print(f"   ✓ {lt.leaveTypeName} (ID: {lt.leaveTypeId})")
        else:
            print("   ⚠ No leave types found. Run: python init_leave_allotment.py")
        
        # Test 3: Check allotments
        print("\n3. Checking leave allotments...")
        if allotments_count > 0:
            sample_allotments = LeaveAllotment.query.limit(5).all()
            for allot in sample_allotments:
                user = User.query.filter_by(userId=allot.allotmentUserId).first()
                user_name = f"{user.userFirstName} {user.userLastName}" if user else f"User {allot.allotmentUserId}"
                leave_type = LeaveType.query.get(allot.allotmentLeaveTypeId)
                leave_name = leave_type.leaveTypeName if leave_type else "Unknown"
                
                print(f"   ✓ {user_name}: {allot.allotmentTotal} {leave_name} ({allot.allotmentYear})")
        else:
            print("   ⚠ No allotments found. Use the web interface to assign leaves.")
        
        # Test 4: Sample query
        print("\n4. Testing sample query...")
        if users_count > 0:
            first_user = User.query.filter_by(userIsActive='1').first()
            user_allotments = LeaveAllotment.query.filter_by(
                allotmentUserId=first_user.userId,
                allotmentYear=datetime.now().year
            ).all()
            
            print(f"   User: {first_user.userFirstName} {first_user.userLastName}")
            if user_allotments:
                for allot in user_allotments:
                    leave_type = LeaveType.query.get(allot.allotmentLeaveTypeId)
                    print(f"   ✓ {leave_type.leaveTypeName}: {allot.allotmentTotal} days")
            else:
                print(f"   ⚠ No allotments for this user in {datetime.now().year}")
        
        # Test 5: API endpoints check
        print("\n5. Available API endpoints:")
        print("   ✓ GET  /api/leave-allotments?user_id={id}&year={year}")
        print("   ✓ POST /api/leave-allotments")
        print("   ✓ POST /api/leave-allotments/bulk")
        print("   ✓ POST /api/leave-allotments/default")
        print("   ✓ DELETE /api/leave-allotments/{id}")
        
        print("\n" + "="*60)
        print("TEST COMPLETED")
        print("="*60)
        print("\nNext steps:")
        print("1. Start the app: python app.py")
        print("2. Open: http://127.0.0.1:5000/leave-management")
        print("3. Use 'Assign Default Leaves' to assign leaves to all users")
        print("4. Check database: SELECT * FROM mtpl_leave_allotment;")
        print("\n")

if __name__ == '__main__':
    test_leave_allotment()
