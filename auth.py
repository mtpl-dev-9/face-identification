import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from models import User
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
print(f"AUTH.PY - SECRET_KEY loaded: {SECRET_KEY[:20]}...")
ACCESS_TOKEN_EXPIRY = 60  # minutes
REFRESH_TOKEN_EXPIRY = 30  # days
def generate_access_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRY),
        'type': 'access'
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
def generate_refresh_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRY),
        'type': 'refresh'
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
def verify_token(token, token_type='access'):
    try:
        import jwt as pyjwt
        payload = pyjwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        if payload.get('type') != token_type:
            return None
        return payload
    except Exception as e:
        print(f"Token verification failed: {str(e)}")
        return None
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'success': False, 'error': 'Token required'}), 401
        if token.startswith('Bearer '):
            token = token[7:]
        payload = verify_token(token)
        if not payload:
            return jsonify({'success': False, 'error': 'Invalid or expired token'}), 401
        user = User.query.filter_by(userId=payload['user_id'], userIsActive='1').first()
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 401
        request.user_id = payload['user_id']
        request.user = user
        return f(*args, **kwargs)
    return decorated
def simple_token_required(f):
    """Simple auth using database stored tokens"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'success': False, 'error': 'Token required'}), 401
        if token.startswith('Bearer '):
            token = token[7:]
        # Check token directly in database
        user = User.query.filter_by(userAccessToken=token, userIsActive='1').first()
        if not user:
            return jsonify({'success': False, 'error': 'Invalid token'}), 401
        request.user_id = user.userId
        request.user = user
        return f(*args, **kwargs)
    return decorated
