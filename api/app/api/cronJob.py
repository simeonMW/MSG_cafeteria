from flask import Blueprint, jsonify#, request

health_bp = Blueprint('health', __name__)

@health_bp.route('/active_injection', methods=['GET'])
def activate():
    return jsonify({"message": "healthy"}), 200