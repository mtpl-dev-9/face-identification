"""User Approvers API - Assign approvers to users"""

def add_user_approvers_routes(app, db):
    from flask import request, jsonify
    from user_approvers_model import UserApprover
    from multilevel_models import LeaveApprover, LeaveApproval
    from models import LeaveRequest, User, get_ist_now

    @app.route("/api/user-approvers", methods=["GET"])
    def api_get_user_approvers():
        """Get all user-approver assignments"""
        user_id = request.args.get('user_id', type=int)
        
        query = UserApprover.query.filter_by(userApproverIsActive=True)
        if user_id:
            query = query.filter_by(userApproverUserId=user_id)
        
        assignments = query.all()
        return jsonify({"success": True, "assignments": [a.to_dict() for a in assignments]})

    @app.route("/api/user-approvers", methods=["POST"])
    def api_assign_approvers_to_user():
        """Assign multiple approvers to a user"""
        data = request.get_json() or {}
        user_id = data.get('user_id')
        approver_ids = data.get('approver_ids', [])
        
        if not user_id or not approver_ids:
            return jsonify({"success": False, "error": "user_id and approver_ids required"}), 400
        
        # Clear existing assignments
        UserApprover.query.filter_by(userApproverUserId=user_id).delete()
        
        # Add new assignments
        assignments = []
        for approver_id in approver_ids:
            assignment = UserApprover(
                userApproverUserId=user_id,
                userApproverApproverId=approver_id
            )
            db.session.add(assignment)
            assignments.append(assignment)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "count": len(assignments),
            "assignments": [a.to_dict() for a in assignments]
        })

    @app.route("/api/user-approvers/<int:assignment_id>", methods=["DELETE"])
    def api_delete_user_approver(assignment_id):
        """Remove approver from user"""
        assignment = UserApprover.query.get(assignment_id)
        if not assignment:
            return jsonify({"success": False, "error": "Assignment not found"}), 404
        
        db.session.delete(assignment)
        db.session.commit()
        
        return jsonify({"success": True})

    @app.route("/api/leave-requests-auto", methods=["POST"])
    def api_create_leave_request_with_auto_approval():
        """Create leave request and auto-assign approvers based on user"""
        from models import LeaveRequest, UserLeaveBalance
        data = request.get_json() or {}
        user_id = data.get('user_id')
        leave_type_id = data.get('leave_type_id')
        from_date_str = data.get('from_date')
        to_date_str = data.get('to_date')
        day_type = data.get('day_type', 'full')
        reason = data.get('reason', '')
        
        if not all([user_id, leave_type_id, from_date_str, to_date_str]):
            return jsonify({"success": False, "error": "All fields required"}), 400
        
        try:
            from datetime import datetime as dt
            from_date = dt.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = dt.strptime(to_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"success": False, "error": "Invalid date format"}), 400
        
        if to_date < from_date:
            return jsonify({"success": False, "error": "To date must be after from date"}), 400
        
        # Calculate days
        base_days = (to_date - from_date).days + 1
        if day_type == 'half' and base_days == 1:
            days = 0.5
        else:
            days = float(base_days)
        
        # Create leave request
        leave_request = LeaveRequest(
            leaveRequestUserId=user_id,
            leaveRequestLeaveTypeId=leave_type_id,
            leaveRequestFromDate=from_date,
            leaveRequestToDate=to_date,
            leaveRequestDays=days,
            leaveRequestReason=reason
        )
        db.session.add(leave_request)
        db.session.flush()  # Get the ID
        
        # Auto-assign approvers based on user's assigned approvers
        user_approvers = UserApprover.query.filter_by(
            userApproverUserId=user_id,
            userApproverIsActive=True
        ).all()
        
        approvals_created = 0
        for user_approver in user_approvers:
            approval = LeaveApproval(
                approvalLeaveRequestId=leave_request.leaveRequestId,
                approvalApproverId=user_approver.userApproverApproverId
            )
            db.session.add(approval)
            approvals_created += 1
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "request": leave_request.to_dict(),
            "approvals_created": approvals_created,
            "message": f"Leave request created with {approvals_created} approvers auto-assigned"
        })

    return app