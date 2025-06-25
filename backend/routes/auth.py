from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
from models.user import User, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        print(f"Registration attempt with data: {data}")
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        # Validate email format
        try:
            valid = validate_email(data['email'])
            email = valid.email
        except EmailNotValidError:
            return jsonify({'message': 'Invalid email format'}), 400
        
        # Check if user already exists
        if User.find_by_email(email):
            return jsonify({'message': 'User with this email already exists'}), 409
        
        # Validate password strength
        password = data['password']
        if len(password) < 6:
            return jsonify({'message': 'Password must be at least 6 characters long'}), 400
        
        # Create new user with correct field mapping
        user = User(
            email=email,
            password=password,
            first_name=data['first_name'],
            last_name=data['last_name'],
            primary_style=data.get('martial_art'),  # Map martial_art to primary_style
            belt_rank=data.get('current_belt')       # Map current_belt to belt_rank
        )
        
        user.save()
        print(f"User created successfully: {user.email}")
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        # Return user data with consistent field names for frontend
        user_data = user.to_dict()
        # Map backend fields to frontend expected fields
        user_data['martial_art'] = user.primary_style
        user_data['current_belt'] = user.belt_rank
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user_data,
            'token': access_token,  # Frontend expects 'token' not 'access_token'
            'refresh_token': refresh_token
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        print(f"Registration error: {str(e)}")
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return tokens"""
    try:
        data = request.get_json()
        print(f"Login attempt with email: {data.get('email')}")
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email and password are required'}), 400
        
        # Find user
        user = User.find_by_email(data['email'])
        if not user:
            print(f"User not found: {data['email']}")
            return jsonify({'message': 'Invalid email or password'}), 401
            
        if not user.check_password(data['password']):
            print(f"Invalid password for user: {data['email']}")
            return jsonify({'message': 'Invalid email or password'}), 401
        
        print(f"Login successful for user: {user.email}")
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        # Return user data with consistent field names for frontend
        user_data = user.to_dict()
        # Map backend fields to frontend expected fields
        user_data['martial_art'] = user.primary_style
        user_data['current_belt'] = user.belt_rank
        
        return jsonify({
            'message': 'Login successful',
            'user': user_data,
            'token': access_token,  # Frontend expects 'token' not 'access_token'
            'refresh_token': refresh_token
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        print(f"Login error: {str(e)}")
        return jsonify({'message': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        new_token = create_access_token(identity=current_user_id)
        
        # Return user data with consistent field names
        user_data = user.to_dict()
        user_data['martial_art'] = user.primary_style
        user_data['current_belt'] = user.belt_rank
        
        return jsonify({
            'token': new_token,  # Frontend expects 'token'
            'user': user_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'message': 'Token refresh failed'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Return user data with consistent field names
        user_data = user.to_dict()
        user_data['martial_art'] = user.primary_style
        user_data['current_belt'] = user.belt_rank
        
        return jsonify({
            'user': user_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get current user error: {str(e)}")
        return jsonify({'message': 'Failed to get user information'}), 500

@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    """Update current user information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'first_name' in data:
            user.first_name = data['first_name'].strip()
        if 'last_name' in data:
            user.last_name = data['last_name'].strip()
        if 'martial_art' in data:
            user.primary_style = data['martial_art']
        if 'current_belt' in data:
            user.belt_rank = data['current_belt']
        
        # Handle email update (requires validation)
        if 'email' in data:
            try:
                valid = validate_email(data['email'])
                new_email = valid.email
                
                # Check if email is already taken by another user
                existing_user = User.find_by_email(new_email)
                if existing_user and existing_user.id != user.id:
                    return jsonify({'message': 'Email already in use'}), 409
                
                user.email = new_email
            except EmailNotValidError:
                return jsonify({'message': 'Invalid email format'}), 400
        
        # Handle password update
        if 'password' in data:
            if len(data['password']) < 6:
                return jsonify({'message': 'Password must be at least 6 characters long'}), 400
            user.set_password(data['password'])
        
        user.save()
        
        # Return user data with consistent field names
        user_data = user.to_dict()
        user_data['martial_art'] = user.primary_style
        user_data['current_belt'] = user.belt_rank
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Update user error: {str(e)}")
        return jsonify({'message': 'Failed to update user'}), 500

@auth_bp.route('/test', methods=['GET'])
def test_auth():
    """Test endpoint for authentication system"""
    return jsonify({
        'message': 'Authentication system is working',
        'timestamp': str(datetime.utcnow())
    }), 200