from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import datetime
from flask import current_app
import re

auth_bp = Blueprint('auth', __name__)

def get_db():
    """Get database instance from current app"""
    return current_app.extensions['sqlalchemy']

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        print(f"Registration attempt with data: {data}")
        
        # Get models from app
        User = current_app.User
        db = get_db()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                print(f"Missing required field: {field}")
                return jsonify({'message': f'{field} is required'}), 400
        
        # Validate email format
        email = data['email'].strip().lower()
        print(f"Validating email: '{email}'")
        
        try:
            from email_validator import validate_email, EmailNotValidError
            valid = validate_email(email)
            email = valid.email
            print(f"Email validation successful: '{email}'")
        except EmailNotValidError as e:
            print(f"Email validation failed: {str(e)}")
            return jsonify({'message': f'Invalid email format: {str(e)}'}), 400
        except ImportError:
            print("email-validator not installed, using basic validation")
            # Basic email validation if email-validator is not available
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                print(f"Basic email validation failed for: '{email}'")
                return jsonify({'message': 'Invalid email format'}), 400
            print(f"Basic email validation successful: '{email}'")
        
        # Check if user already exists
        existing_user = User.find_by_email(email)
        if existing_user:
            print(f"User already exists with email: {email}")
            return jsonify({'message': 'User with this email already exists'}), 409
        
        # Validate password strength
        password = data['password']
        if len(password) < 6:
            print(f"Password too short: {len(password)} characters")
            return jsonify({'message': 'Password must be at least 6 characters long'}), 400
        
        # Create new user with correct field mapping
        user = User(
            email=email,
            password=password,
            first_name=data['first_name'],
            last_name=data['last_name'],
            primary_style=data.get('martial_art'),  # Map martial_art to primary_style
            belt_rank=data.get('current_belt'),     # Map current_belt to belt_rank
            dojo=data.get('dojo')
        )
        
        user.save()
        print(f"User created successfully: {user.email} with ID: {user.id}")
        
        # Create tokens - CONVERT USER ID TO STRING
        access_token = create_access_token(identity=str(user.id))  # Convert to string!
        refresh_token = create_refresh_token(identity=str(user.id))  # Convert to string!
        
        print(f"Tokens created successfully - Access token: {access_token[:20]}...")
        
        # Return user data with consistent field names for frontend
        user_data = user.to_dict()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user_data,
            'token': access_token,  # Frontend expects 'token' not 'access_token'
            'refresh_token': refresh_token
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        print(f"Registration error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return tokens"""
    try:
        data = request.get_json()
        print(f"Login attempt with email: {data.get('email')}")
        
        # Get models from app
        User = current_app.User
        db = get_db()
        
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
        
        print(f"Login successful for user: {user.email} with ID: {user.id}")
        
        # Create tokens - CONVERT USER ID TO STRING
        access_token = create_access_token(identity=str(user.id))  # Convert to string!
        refresh_token = create_refresh_token(identity=str(user.id))  # Convert to string!
        
        print(f"Tokens created with string identity: {str(user.id)}")
        
        # Return user data with consistent field names for frontend
        user_data = user.to_dict()
        
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
        current_user_id = get_jwt_identity()  # This will now be a string
        print(f"Refreshing token for user ID: {current_user_id}")
        
        User = current_app.User
        
        # Convert string back to int for database query
        user = User.query.get(int(current_user_id))
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Create new token with string identity
        new_token = create_access_token(identity=current_user_id)  # Keep as string
        
        # Return user data with consistent field names
        user_data = user.to_dict()
        
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
        current_user_id = get_jwt_identity()  # This will now be a string
        print(f"Getting current user with ID: {current_user_id}")
        
        User = current_app.User
        
        # Convert string back to int for database query
        user = User.query.get(int(current_user_id))
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Return user data with consistent field names
        user_data = user.to_dict()
        
        return jsonify({
            'user': user_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get current user error: {str(e)}")
        print(f"Get current user error: {str(e)}")
        return jsonify({'message': 'Failed to get user information'}), 500

@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    """Update current user information"""
    try:
        current_user_id = get_jwt_identity()  # This will now be a string
        User = current_app.User
        db = get_db()
        
        # Convert string back to int for database query
        user = User.query.get(int(current_user_id))
        
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
        if 'dojo' in data:
            user.dojo = data['dojo']
        
        # Handle email update (requires validation)
        if 'email' in data:
            try:
                from email_validator import validate_email, EmailNotValidError
                valid = validate_email(data['email'])
                new_email = valid.email
                
                # Check if email is already taken by another user
                existing_user = User.find_by_email(new_email)
                if existing_user and existing_user.id != user.id:
                    return jsonify({'message': 'Email already in use'}), 409
                
                user.email = new_email
            except EmailNotValidError:
                return jsonify({'message': 'Invalid email format'}), 400
            except ImportError:
                # Basic email validation
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, data['email']):
                    return jsonify({'message': 'Invalid email format'}), 400
                user.email = data['email'].strip().lower()
        
        # Handle password update
        if 'password' in data:
            if len(data['password']) < 6:
                return jsonify({'message': 'Password must be at least 6 characters long'}), 400
            user.set_password(data['password'])
        
        user.save()
        
        # Return user data with consistent field names
        user_data = user.to_dict()
        
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

# Debug endpoint to test JWT token
@auth_bp.route('/test-jwt', methods=['GET'])
@jwt_required()
def test_jwt():
    """Test endpoint for JWT authentication"""
    try:
        current_user_id = get_jwt_identity()  # This will now be a string
        print(f"JWT test successful for user ID: {current_user_id}")
        return jsonify({
            'message': 'JWT authentication is working',
            'user_id': current_user_id,
            'user_id_type': type(current_user_id).__name__,
            'timestamp': str(datetime.utcnow())
        }), 200
    except Exception as e:
        print(f"JWT test error: {str(e)}")
        return jsonify({'message': f'JWT test failed: {str(e)}'}), 500
    
@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """Get user profile - alias for /me endpoint"""
    return get_current_user()

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    """Update user profile - alias for /me endpoint"""
    return update_current_user()

# Also add this route to match frontend expectations
@auth_bp.route('/user/profile', methods=['GET'])
@jwt_required()
def get_user_profile_alt():
    """Alternative profile endpoint to match frontend"""
    return get_current_user()

@auth_bp.route('/user/profile', methods=['PUT'])
@jwt_required()
def update_user_profile_alt():
    """Alternative profile update endpoint to match frontend"""
    return update_current_user()