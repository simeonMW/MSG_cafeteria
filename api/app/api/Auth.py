from flask import Blueprint, request, jsonify
from app.services.authService import AuthService
from app.security import role_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Endpoint for Process 1.1: Registration.
    """
    data = request.get_json()
    
    # Required fields validation (Basic Control)
    required = ['email', 'password', 'role']
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    user, msg = AuthService.register_user(data)
    if not user:
        return jsonify({"error": msg}), 409 # Conflict

    return jsonify({
        "message": msg,
        "user_id": user.id
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Endpoint for Process 1.2: Authentication.
    Validates credentials and issues the JWT for mobile/web apps.
    """
    data = request.get_json()
    
    result, msg = AuthService.login_user(data)
    if not result:
        return jsonify({"error": msg}), 401 # Unauthorized

    return jsonify({
        "message": msg,
        "token": result['token'],
        "user": result['user']
    }), 200

@auth_bp.route('/verify-user/<int:user_id>', methods=['POST'])
@role_required(['hr_manager'])
def verify_user(user_id):
    """
    Endpoint for Process 1.3: Verification.
    Strictly protected; only the HR Web App can trigger this.
    """
    # The role_required decorator ensures request.user is populated via JWT
    admin_role = request.user.get('role')
    
    success, msg = AuthService.verify_account(user_id, admin_role)
    if not success:
        return jsonify({"error": msg}), 400

    return jsonify({"message": msg}), 200

@auth_bp.route('/me', methods=['GET'])
@role_required(['customer', 'chef', 'hr_manager'])
def get_current_user():
    """
    Helper endpoint to validate the token and return current session data.
    """
    from app.repositories.userRepo import UserRepo
    user = UserRepo.get_by_id(request.user['user_id'])
    return jsonify(user.to_dict()), 200