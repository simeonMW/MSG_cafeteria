import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app,  redirect, session, url_for


# --- PASSWORD HASHING (Process 1.1) ---

def hash_pwd(password):
    """
    Control: Never store plain text.
    Uses Bcrypt with a salt to protect against rainbow table attacks.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_pwd(password, hashed):
    """
    Validates a login attempt by comparing hashes.
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# --- JWT MANAGEMENT (Process 1.2) ---

def generate_token(user_id, role):
    """
    Generates a secure identity token.
    The payload includes the user ID and role for authorization.
    """
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

# --- AUTHORIZATION DECORATORS (Access Control) ---

def role_required(allowed_roles):
    """
    Verifies the JWT and ensures the user's role matches the endpoint requirements.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            
            # Check for Authorization header
            if 'Authorization' in request.headers:
                # Format: "Bearer <token>"
                auth_header = request.headers['Authorization'].split(" ")
                if len(auth_header) == 2:
                    token = auth_header[1]
            elif session['admin_token']:
                token = session['admin_token']

            if not token:
                if allowed_roles == ['hr_manager']:
                    return redirect(url_for('dashboard.signin'))
                return jsonify({"error": "Authentication token is missing"}), 401

            try:
                # Decode and verify the signature
                data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                
                # Role Check
                if data['role'] not in allowed_roles:
                    if allowed_roles == ['hr_manager']:
                        return redirect(url_for('dashboard.signin'))
                    return jsonify({"error": "Access denied: Unauthorized role"}), 403
                
                # user data into the request object for use
                request.user = data
                
            except jwt.ExpiredSignatureError:
                if allowed_roles == ['hr_manager']:
                    return redirect(url_for('dashboard.signin'))
                return jsonify({"error": "Token has expired. Please log in again."}), 401
            except jwt.InvalidTokenError:
                if allowed_roles == ['hr_manager']:
                    return redirect(url_for('dashboard.signin'))
                return jsonify({"error": "Invalid token. Access denied."}), 401

            return f(*args, **kwargs)
        return decorated_function
    return decorator