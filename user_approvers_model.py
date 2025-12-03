"""User Approvers Model"""
from datetime import datetime
from database import db
import pytz

IST = pytz.timezone('Asia/Kolkata')

def get_ist_now():
    return datetime.now(IST)


class UserApprover(db.Model):
    __tablename__ = "mtpl_user_approvers"

    userApproverId = db.Column('userApproverId', db.Integer, primary_key=True)
    userApproverUserId = db.Column('userApproverUserId', db.Integer, nullable=False, index=True)
    userApproverApproverId = db.Column('userApproverApproverId', db.Integer, nullable=False, index=True)
    userApproverIsActive = db.Column('userApproverIsActive', db.Boolean, default=True)
    userApproverCreatedAt = db.Column('userApproverCreatedAt', db.DateTime, default=get_ist_now)

    def to_dict(self):
        from multilevel_models import LeaveApprover
        from models import User
        
        approver = LeaveApprover.query.get(self.userApproverApproverId)
        user = User.query.get(self.userApproverUserId)
        
        return {
            "id": self.userApproverId,
            "user_id": self.userApproverUserId,
            "user_name": f"{user.userFirstName} {user.userLastName}" if user else "Unknown",
            "approver_id": self.userApproverApproverId,
            "approver_name": approver.approverName if approver else "Unknown",
            "approver_role": approver.approverRole if approver else "Unknown",
            "is_active": self.userApproverIsActive,
            "created_at": self.userApproverCreatedAt.isoformat() + "Z"
        }