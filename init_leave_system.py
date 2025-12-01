"""
Initialize Leave Management System
Run this script once to set up default leave types and sample data
"""

from app import create_app
from database import db
from models import LeaveType, UserLeaveBalance, User
from datetime import datetime

def init_leave_system():
    app = create_app()
    
    with app.app_context():
        print("🚀 Initializing Leave Management System...")
        
        # Create tables
        db.create_all()
        print("✅ Database tables created")
        
        # Default leave types
        default_leave_types = [
            "Casual Leave",
            "Sick Leave",
            "Celebratory Leave",
            "Earned Leave",
            "Maternity Leave",
            "Paternity Leave"
        ]
        
        print("\n📋 Creating default leave types...")
        for leave_name in default_leave_types:
            existing = LeaveType.query.filter_by(leaveTypeName=leave_name).first()
            if not existing:
                leave_type = LeaveType(leaveTypeName=leave_name)
                db.session.add(leave_type)
                print(f"  ✓ Added: {leave_name}")
            else:
                print(f"  ⊙ Exists: {leave_name}")
        
        db.session.commit()
        print("\n✅ Leave types initialized successfully!")
        
        # Optional: Assign sample leave balances
        print("\n📊 Sample Leave Balance Assignment")
        print("=" * 50)
        
        users = User.query.filter_by(userIsActive='1').limit(5).all()
        if users:
            print(f"Found {len(users)} active users")
            assign_sample = input("\nAssign sample leave balances? (y/n): ").lower()
            
            if assign_sample == 'y':
                current_year = datetime.now().year
                leave_types = LeaveType.query.filter_by(leaveTypeIsActive=True).all()
                
                # Default allocation
                leave_allocation = {
                    "Casual Leave": 12,
                    "Sick Leave": 10,
                    "Celebratory Leave": 3,
                    "Earned Leave": 15,
                    "Maternity Leave": 180,
                    "Paternity Leave": 15
                }
                
                for user in users:
                    print(f"\n  Assigning to: {user.name} (ID: {user.userId})")
                    
                    for leave_type in leave_types:
                        total_leaves = leave_allocation.get(leave_type.leaveTypeName, 10)
                        
                        existing = UserLeaveBalance.query.filter_by(
                            balanceUserId=user.userId,
                            balanceLeaveTypeId=leave_type.leaveTypeId,
                            balanceYear=current_year
                        ).first()
                        
                        if not existing:
                            balance = UserLeaveBalance(
                                balanceUserId=user.userId,
                                balanceLeaveTypeId=leave_type.leaveTypeId,
                                balanceTotal=total_leaves,
                                balanceYear=current_year
                            )
                            db.session.add(balance)
                            print(f"    ✓ {leave_type.leaveTypeName}: {total_leaves} days")
                
                db.session.commit()
                print("\n✅ Sample balances assigned!")
        else:
            print("No active users found. Register employees first.")
        
        print("\n" + "=" * 50)
        print("🎉 Leave Management System Ready!")
        print("=" * 50)
        print("\n📍 Access at: http://127.0.0.1:5000/leave-management")
        print("\n📚 Read LEAVE_MANAGEMENT_GUIDE.md for usage instructions")

if __name__ == "__main__":
    init_leave_system()
