from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import secrets
from models import db, User, PasswordResetToken
from config import Config
from utils.email import send_reset_email

auth_bp = Blueprint('auth', __name__)

# ✅ Add this helper function at the top (after imports)
def get_user_from_token():
    """Extract and validate user from JWT token"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None, {'message': 'Authorization token required'}, 401

    token = auth_header.split(' ')[1]

    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        user = User.query.get(user_id)

        if not user:
            return None, {'message': 'User not found'}, 404

        return user, None, None
    except jwt.ExpiredSignatureError:
        return None, {'message': 'Token has expired'}, 401
    except jwt.InvalidTokenError:
        return None, {'message': 'Invalid token'}, 401

# ✅ Add this new endpoint
@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """
    Get Current User
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Current user information
        schema:
          type: object
          properties:
            user:
              $ref: '#/definitions/User'
      401:
        description: Unauthorized
      404:
        description: User not found
    """
    user, error, status_code = get_user_from_token()

    if error:
        return jsonify(error), status_code

    return jsonify({'user': user.to_dict()}), 200

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    User Signup
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          $ref: '#/definitions/SignupRequest'
    responses:
      201:
        description: User created successfully
      400:
        description: Missing required fields
      409:
        description: User already exists
      500:
        description: Server error
    """
    data = request.get_json()

    # Validation
    if not data.get('email') or not data.get('password') or not data.get('fullName'):
        return jsonify({'message': 'Email, password, and full name are required'}), 400

    # Check if user exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'User already exists'}), 409

    # Create new user
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(
        email=data['email'],
        password_hash=hashed_password,
        full_name=data['fullName'],
        company=data.get('company', '')
    )

    try:
        db.session.add(new_user)
        db.session.commit()

        # Generate token
        token = jwt.encode({
            'user_id': new_user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=Config.JWT_EXPIRATION_DAYS)
        }, Config.SECRET_KEY, algorithm='HS256')

        return jsonify({
            'message': 'User created successfully',
            'token': token,
            'user': new_user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating user', 'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User Login
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          $ref: '#/definitions/LoginRequest'
    responses:
      200:
        description: Login successful
      400:
        description: Missing required fields
      401:
        description: Invalid email or password
    """
    data = request.get_json()

    if not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password are required'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'message': 'Invalid email or password'}), 401

    # Generate token
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=Config.JWT_EXPIRATION_DAYS)
    }, Config.SECRET_KEY, algorithm='HS256')

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Request Password Reset
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
          properties:
            email:
              type: string
              example: "user@example.com"
    responses:
      200:
        description: Reset email sent
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Password reset email sent"
      400:
        description: Missing email
      404:
        description: User not found
      500:
        description: Server error
    """
    data = request.get_json()

    if not data.get('email'):
        return jsonify({'message': 'Email is required'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user:
        # Return success even if user doesn't exist (security best practice)
        return jsonify({'message': 'If an account exists, a password reset email has been sent'}), 200

    try:
        # Generate secure random token
        reset_token = secrets.token_urlsafe(32)

        # Delete any existing reset tokens for this user
        PasswordResetToken.query.filter_by(user_id=user.id).delete()

        # Create new reset token (expires in 1 hour)
        token_record = PasswordResetToken(
            user_id=user.id,
            token=reset_token,
            expires_at=datetime.datetime.utcnow() + datetime.timedelta(days=Config.PASSWORD_RESET_TOKEN_EXPIRATION_DAYS)
        )

        db.session.add(token_record)
        db.session.commit()

        # Send reset email
        reset_url = f"{Config.FRONTEND_URL}/reset-password?token={reset_token}"
        send_reset_email(user.email, user.full_name, reset_url)

        return jsonify({'message': 'If an account exists, a password reset email has been sent'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error processing request', 'error': str(e)}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Reset Password
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - token
            - newPassword
          properties:
            token:
              type: string
              example: "abc123xyz..."
            newPassword:
              type: string
              example: "NewSecurePassword123!"
    responses:
      200:
        description: Password reset successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Password reset successful"
      400:
        description: Missing required fields or invalid token
      500:
        description: Server error
    """
    data = request.get_json()

    if not data.get('token') or not data.get('newPassword'):
        return jsonify({'message': 'Token and new password are required'}), 400

    # Find valid token
    token_record = PasswordResetToken.query.filter_by(
        token=data['token'],
        used=False
    ).first()

    if not token_record:
        return jsonify({'message': 'Invalid or expired token'}), 400

    # Check if token has expired
    if token_record.expires_at < datetime.datetime.utcnow():
        return jsonify({'message': 'Token has expired'}), 400

    try:
        # Update user password
        user = User.query.get(token_record.user_id)
        user.password_hash = generate_password_hash(data['newPassword'], method='pbkdf2:sha256')

        # Mark token as used
        token_record.used = True

        db.session.commit()

        return jsonify({'message': 'Password reset successful'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error resetting password', 'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """
    Change Password (for authenticated users)
    ---
    tags:
      - Authentication
    parameters:
      - name: Authorization
        in: header
        required: true
        type: string
        description: Bearer token
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - currentPassword
            - newPassword
          properties:
            currentPassword:
              type: string
            newPassword:
              type: string
    responses:
      200:
        description: Password changed successfully
      400:
        description: Missing required fields
      401:
        description: Invalid current password or unauthorized
      500:
        description: Server error
    """
    # Get token from header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'message': 'Authorization token required'}), 401

    token = auth_header.split(' ')[1]

    try:
        # Decode token
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401

    data = request.get_json()

    if not data.get('currentPassword') or not data.get('newPassword'):
        return jsonify({'message': 'Current password and new password are required'}), 400

    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Verify current password
    if not check_password_hash(user.password_hash, data['currentPassword']):
        return jsonify({'message': 'Current password is incorrect'}), 401

    try:
        # Update password
        user.password_hash = generate_password_hash(data['newPassword'], method='pbkdf2:sha256')
        db.session.commit()

        return jsonify({'message': 'Password changed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error changing password', 'error': str(e)}), 500