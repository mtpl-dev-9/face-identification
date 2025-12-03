"""Multi-Level Approval API Routes"""

def add_multilevel_approval_routes(app, db):
    from flask import request, jsonify
    from multilevel_models import LeaveApprover, LeaveApproval
    from models import LeaveRequest, get_ist_now
    from sqlalchemy import and_

    # ===== APPROVER MANAGEMENT =====
    
    @app.route("/api/leave-approvers", methods=["GET"])
    def api_get_leave_approvers():
        """
        Get All Leave Approvers
        ---
        tags:
          - Multi-Level Approval
        responses:
          200:
            description: List of active leave approvers
        """
        approvers = LeaveApprover.query.filter_by(approverIsActive=True).all()
        return jsonify({"success": True, "approvers": [a.to_dict() for a in approvers]})

    @app.route("/api/leave-approvers", methods=["POST"])
    def api_add_leave_approver():
        """
        Add Leave Approver
        ---
        tags:
          - Multi-Level Approval
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                user_id:
                  type: integer
                name:
                  type: string
                role:
                  type: string
                  enum: [Admin, HR, Manager, Director]
        responses:
          200:
            description: Approver added successfully
        """
        data = request.get_json() or {}
        user_id = data.get('user_id')
        name = data.get('name')
        role = data.get('role', 'Manager')
        
        if not user_id or not name:
            return jsonify({"success": False, "error": "user_id and name required"}), 400
        
        # Allow same user with different roles
        existing = LeaveApprover.query.filter_by(approverUserId=user_id, approverRole=role).first()
        if existing:
            return jsonify({"success": False, "error": f"User already exists as {role}"}), 400
        
        approver = LeaveApprover(
            approverUserId=user_id,
            approverName=name,
            approverRole=role
        )
        db.session.add(approver)
        db.session.commit()
        
        return jsonify({"success": True, "approver": approver.to_dict()})

    @app.route("/api/leave-approvers/<int:approver_id>", methods=["DELETE"])
    def api_delete_leave_approver(approver_id):
        """Delete Leave Approver"""
        approver = LeaveApprover.query.get(approver_id)
        if not approver:
            return jsonify({"success": False, "error": "Approver not found"}), 404
        
        approver.approverIsActive = False
        db.session.commit()
        
        return jsonify({"success": True})

    # ===== MULTI-LEVEL APPROVAL WORKFLOW =====
    
    @app.route("/api/leave-requests/<int:request_id>/assign-approvers", methods=["POST"])
    def api_assign_approvers_to_request(request_id):
        """
        Assign Multiple Approvers to Leave Request
        ---
        tags:
          - Multi-Level Approval
        parameters:
          - name: request_id
            in: path
            type: integer
            required: true
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                approver_ids:
                  type: array
                  items:
                    type: integer
        responses:
          200:
            description: Approvers assigned to request
        """
        data = request.get_json() or {}
        approver_ids = data.get('approver_ids', [])
        
        if not approver_ids:
            return jsonify({"success": False, "error": "approver_ids required"}), 400
        
        leave_request = LeaveRequest.query.get(request_id)
        if not leave_request:
            return jsonify({"success": False, "error": "Leave request not found"}), 404
        
        # Clear existing approvals
        LeaveApproval.query.filter_by(approvalLeaveRequestId=request_id).delete()
        
        # Add new approvals
        approvals = []
        for approver_id in approver_ids:
            approval = LeaveApproval(
                approvalLeaveRequestId=request_id,
                approvalApproverId=approver_id,
                approvalUserId=leave_request.leaveRequestUserId
            )
            db.session.add(approval)
            approvals.append(approval)
        
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "count": len(approvals),
            "approvals": [a.to_dict() for a in approvals]
        })

    @app.route("/api/leave-requests/<int:request_id>/approvals", methods=["GET"])
    def api_get_request_approvals(request_id):
        """
        Get All Approvals for Leave Request
        ---
        tags:
          - Multi-Level Approval
        parameters:
          - name: request_id
            in: path
            type: integer
            required: true
        responses:
          200:
            description: List of approvals with summary
        """
        approvals = LeaveApproval.query.filter_by(approvalLeaveRequestId=request_id).all()
        
        # Calculate overall status
        total_approvals = len(approvals)
        approved_count = len([a for a in approvals if a.approvalStatus == 'approved'])
        rejected_count = len([a for a in approvals if a.approvalStatus == 'rejected'])
        
        if rejected_count > 0:
            overall_status = "rejected"
        elif approved_count == total_approvals and total_approvals > 0:
            overall_status = "fully_approved"
        elif approved_count > 0:
            overall_status = "partial_approved"
        else:
            overall_status = "pending"
        
        return jsonify({
            "success": True,
            "approvals": [a.to_dict() for a in approvals],
            "summary": {
                "total": total_approvals,
                "approved": approved_count,
                "rejected": rejected_count,
                "pending": total_approvals - approved_count - rejected_count,
                "overall_status": overall_status
            }
        })

    @app.route("/api/leave-approvals/<int:approval_id>/approve", methods=["POST"])
    def api_approve_individual_approval(approval_id):
        """
        Approve Individual Approval
        ---
        tags:
          - Multi-Level Approval
        parameters:
          - name: approval_id
            in: path
            type: integer
            required: true
          - name: body
            in: body
            schema:
              type: object
              properties:
                comments:
                  type: string
        responses:
          200:
            description: Approval approved successfully
        """
        data = request.get_json() or {}
        comments = data.get('comments', '')
        
        approval = LeaveApproval.query.get(approval_id)
        if not approval:
            return jsonify({"success": False, "error": "Approval not found"}), 404
        
        if approval.approvalStatus != 'pending':
            return jsonify({"success": False, "error": "Already processed"}), 400
        
        approval.approvalStatus = 'approved'
        approval.approvalComments = comments
        approval.approvalApprovedAt = get_ist_now()
        
        # Check if all approvals are done
        all_approvals = LeaveApproval.query.filter_by(
            approvalLeaveRequestId=approval.approvalLeaveRequestId
        ).all()
        
        all_approved = all([a.approvalStatus == 'approved' for a in all_approvals])
        any_rejected = any([a.approvalStatus == 'rejected' for a in all_approvals])
        
        # Update leave request status
        leave_request = LeaveRequest.query.get(approval.approvalLeaveRequestId)
        if any_rejected:
            leave_request.leaveRequestStatus = 'rejected'
        elif all_approved:
            leave_request.leaveRequestStatus = 'approved'
            # Deduct from balance here if needed
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "approval": approval.to_dict(),
            "all_approved": all_approved,
            "request_status": leave_request.leaveRequestStatus
        })

    @app.route("/api/leave-approvals/<int:approval_id>/reject", methods=["POST"])
    def api_reject_individual_approval(approval_id):
        """
        Reject Individual Approval
        ---
        tags:
          - Multi-Level Approval
        parameters:
          - name: approval_id
            in: path
            type: integer
            required: true
          - name: body
            in: body
            schema:
              type: object
              properties:
                comments:
                  type: string
        responses:
          200:
            description: Approval rejected successfully
        """
        data = request.get_json() or {}
        comments = data.get('comments', '')
        
        approval = LeaveApproval.query.get(approval_id)
        if not approval:
            return jsonify({"success": False, "error": "Approval not found"}), 404
        
        if approval.approvalStatus != 'pending':
            return jsonify({"success": False, "error": "Already processed"}), 400
        
        approval.approvalStatus = 'rejected'
        approval.approvalComments = comments
        approval.approvalApprovedAt = get_ist_now()
        
        # Reject the entire leave request
        leave_request = LeaveRequest.query.get(approval.approvalLeaveRequestId)
        leave_request.leaveRequestStatus = 'rejected'
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "approval": approval.to_dict(),
            "request_status": leave_request.leaveRequestStatus
        })

    @app.route("/api/my-pending-approvals/<int:approver_user_id>", methods=["GET"])
    def api_get_my_pending_approvals(approver_user_id):
        """Get Pending Approvals for Specific Approver"""
        # Find approver
        approver = LeaveApprover.query.filter_by(
            approverUserId=approver_user_id,
            approverIsActive=True
        ).first()
        
        if not approver:
            return jsonify({"success": False, "error": "Not an approver"}), 404
        
        # Get pending approvals
        pending_approvals = LeaveApproval.query.filter_by(
            approvalApproverId=approver.approverId,
            approvalStatus='pending'
        ).all()
        
        # Get leave request details
        results = []
        for approval in pending_approvals:
            leave_request = LeaveRequest.query.get(approval.approvalLeaveRequestId)
            if leave_request:
                result = approval.to_dict()
                result['leave_request'] = leave_request.to_dict()
                results.append(result)
        
        return jsonify({
            "success": True,
            "approver": approver.to_dict(),
            "pending_approvals": results
        })

    return app