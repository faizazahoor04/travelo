from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask import jsonify

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            return f(current_user_id, *args, **kwargs)
        except Exception as e:
            return jsonify({"error": "Token is invalid or expired"}), 401
    return decorated