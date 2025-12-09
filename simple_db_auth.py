"""
Simple database token authentication
Just checks user_id and access_token from mtpl_users table
"""
from functools import wraps
from flask import request, jsonify
from models import User

def simple_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'success': False, 'error': 'Authorization header required'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        # Check if token exists in database for any active user
        user = User.query.filter_by(userAccessToken=token, userIsActive='1').first()
        if not user:
            return jsonify({'success': False, 'error': 'Invalid or expired token'}), 401
        
        # Set user info in request for use in endpoint
        request.user_id = user.userId
        request.user = user
        return f(*args, **kwargs)
    return decorated