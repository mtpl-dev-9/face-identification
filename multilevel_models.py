"""Multi-Level Approval Models"""
from datetime import datetime
from database import db
import pytz

IST = pytz.timezone('Asia/Kolkata')

def get_ist_now():
    return datetime.now(IST)


class LeaveApprover(db.Model):
    __tablename__ = "mtpl_leave_approvers"

    approverId = db.Column('approverId', db.Integer, primary_key=True)
    approverUserId = db.Column('approverUserId', db.Integer, nullable=False, index=True)
    approverName = db.Column('approverName', db.String(100), nullable=False)
    approverRole = db.Column('approverRole', db.String(50), default='Manager')
    approverIsActive = db.Column('approverIsActive', db.Boolean, default=True)
    approverCreatedAt = db.Column('approverCreatedAt', db.DateTime, default=get_ist_now)

    def to_dict(self):
        return {
            "id": self.approverId,
            "user_id": self.approverUserId,
            "name": self.approverName,
            "role": self.approverRole,
            "is_active": self.approverIsActive,
            "created_at": self.approverCreatedAt.isoformat() + "Z"
        }


class LeaveApproval(db.Model):
    __tablename__ = "mtpl_leave_approvals"

    approvalId = db.Column('approvalId', db.Integer, primary_key=True)
    approvalLeaveRequestId = db.Column('approvalLeaveRequestId', db.Integer, nullable=False, index=True)
    approvalApproverId = db.Column('approvalApproverId', db.Integer, nullable=False, index=True)
    approvalUserId = db.Column('approvalUserId', db.Integer, nullable=True, index=True)
    approvalStatus = db.Column('approvalStatus', db.Enum('pending', 'approved', 'rejected'), default='pending')
    approvalComments = db.Column('approvalComments', db.Text)
    approvalApprovedAt = db.Column('approvalApprovedAt', db.DateTime, nullable=True)
    approvalCreatedAt = db.Column('approvalCreatedAt', db.DateTime, default=get_ist_now)

    def to_dict(self):
        approver = LeaveApprover.query.get(self.approvalApproverId)
        from models import User
        user = User.query.get(self.approvalUserId) if self.approvalUserId else None
        
        return {
            "id": self.approvalId,
            "leave_request_id": self.approvalLeaveRequestId,
            "approver_id": self.approvalApproverId,
            "approver_name": approver.approverName if approver else "Unknown",
            "approver_role": approver.approverRole if approver else "Unknown",
            "user_id": self.approvalUserId,
            "user_name": f"{user.userFirstName} {user.userLastName}" if user else "Unknown",
            "status": self.approvalStatus,
            "comments": self.approvalComments,
            "approved_at": self.approvalApprovedAt.isoformat() + "Z" if self.approvalApprovedAt else None,
            "created_at": self.approvalCreatedAt.isoformat() + "Z"
        }