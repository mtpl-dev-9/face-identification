"""Test User Approvers API"""
from app import create_app
from flask import request, jsonify

app = create_app()

@app.route("/api/test-user-approvers", methods=["GET"])
def test_user_approvers():
    return jsonify({"success": True, "message": "User approvers API is working"})

@app.route("/api/user-approvers-simple", methods=["GET"])
def api_get_user_approvers_simple():
    """Simple test version"""
    try:
        from user_approvers_model import UserApprover
        assignments = UserApprover.query.all()
        return jsonify({
            "success": True, 
            "count": len(assignments),
            "assignments": [{"id": a.userApproverId, "user_id": a.userApproverUserId, "approver_id": a.userApproverApproverId} for a in assignments]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/user-approvers-simple", methods=["POST"])
def api_assign_approvers_simple():
    """Simple test version"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        approver_ids = data.get('approver_ids', [])
        
        if not user_id or not approver_ids:
            return jsonify({"success": False, "error": "user_id and approver_ids required"}), 400
        
        from user_approvers_model import UserApprover
        from database import db
        
        # Clear existing
        UserApprover.query.filter_by(userApproverUserId=user_id).delete()
        
        # Add new
        count = 0
        for approver_id in approver_ids:
            assignment = UserApprover(
                userApproverUserId=user_id,
                userApproverApproverId=approver_id
            )
            db.session.add(assignment)
            count += 1
        
        db.session.commit()
        
        return jsonify({"success": True, "count": count})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)