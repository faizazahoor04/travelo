from flask import Blueprint, request, jsonify
from app import db
from app.models.models import User
from flask_jwt_extended import create_access_token
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate request data
        if not data:
            return jsonify({"error": "Request body required"}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        username = data.get('username', email.split('@')[0] if email else '').strip()
        
        # Validate required fields
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # Basic email validation
        if '@' not in email or '.' not in email:
            return jsonify({"error": "Invalid email format"}), 400
        
        # Validate password strength
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "User with this email already exists"}), 409
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already taken"}), 409
        
        # Create new user
        user = User(
            username=username,
            email=email
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.flush()  # Get the user ID without committing
        
        # Create default preferences
        from app.models.models import UserPreference
        pref = UserPreference(user_id=user.id, max_budget=100)
        db.session.add(pref)
        db.session.commit()
        
        # Generate JWT token
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=7))
        
        logger.info(f"New user registered: {email}")
        
        return jsonify({
            "message": "User created successfully",
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "token": token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Signup error: {str(e)}")
        return jsonify({"error": "An error occurred during signup"}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token"""
    try:
        data = request.get_json()
        
        # Validate request data
        if not data:
            return jsonify({"error": "Request body required"}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        # Validate required fields
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        # Check password
        if user and user.check_password(password):
            token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=7))
            
            logger.info(f"User logged in: {email}")
            
            return jsonify({
                "message": "Login successful",
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "token": token
            }), 200
        
        logger.warning(f"Failed login attempt for email: {email}")
        return jsonify({"error": "Invalid email or password"}), 401
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({"error": "An error occurred during login"}), 500


@auth_bp.route('/validate', methods=['GET'])
def validate_token():
    """Validate if token is still valid"""
    try:
        from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
        
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "valid": True,
            "user_id": user.id,
            "username": user.username,
            "email": user.email
        }), 200
        
    except Exception as e:
        logger.warning(f"Token validation error: {str(e)}")
        return jsonify({"error": "Token is invalid or expired"}), 401