from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)

""" @health_bp.route('/active_injection', methods=['GET'])
def activate():
    return jsonify({"status": "alive"}), 200 """

@health_bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "alive"}), 200