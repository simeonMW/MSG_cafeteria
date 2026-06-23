from flask import Blueprint, request, jsonify
from app.services.orderService import OrderService
from app.security import role_required
from app.supabase_client import SupabaseStorage

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/place', methods=['POST'])
@role_required(['customer'])
def place_order():
    """
    Endpoint for Process 3.2 & 3.3.
    Triggered by the Customer Mobile App.
    """
    data = request.get_json()
    item_id = data.get('item_id')
    
    if not item_id:
        return jsonify({"error": "Item ID is required to place an order"}), 400

    # User ID is extracted from the secure JWT by the decorator
    user_id = request.user.get('user_id')
    
    transaction, msg = OrderService.place_order(user_id, item_id)
    
    if not transaction:
        return jsonify({"error": msg}), 400

    signed_url = SupabaseStorage.create_signed_url(transaction.qr_code_path, expires_in=300)

    return jsonify({
        "message": msg,
        "transaction_id": transaction.id,
        "token": transaction.token,
        "qr_code_url": signed_url,
        "price_charged": transaction.order_price
    }), 201

@orders_bp.route('/verify', methods=['POST'])
@role_required(['chef'])
def verify_order():
    """
    Endpoint for Process 3.4: Validate.
    Triggered when the Chef scans the Customer's QR code.
    """
    data = request.get_json()
    token = data.get('token')

    if not token:
        return jsonify({"error": "No token provided for validation"}), 400

    role = request.user.get('role')
    success, msg = OrderService.validate_fulfillment(token, role)

    if not success:
        return jsonify({"error": msg}), 400

    return jsonify({"message": msg}), 200

@orders_bp.route('/history', methods=['GET'])
@role_required(['customer'])
def get_history():
    """
    Returns the order history for the logged-in customer.
    """
    user_id = request.user.get('user_id')
    history = OrderService.get_customer_history(user_id)
    return jsonify([tx.to_dict() for tx in history]), 200

@orders_bp.route('/<int:transaction_id>/qr', methods=['GET'])
@role_required(['customer'])
def get_transaction_qr(transaction_id):
    """
    Returns a time-limited signed URL for the requested transaction QR code.
    """
    user_id = request.user.get('user_id')
    transaction = OrderService.get_transaction_by_id(transaction_id)

    if not transaction or transaction.customer_id != user_id:
        return jsonify({"error": "Transaction not found or access denied."}), 404

    signed_url = SupabaseStorage.create_signed_url(transaction.qr_code_path, expires_in=300)
    return jsonify({"qr_code_url": signed_url}), 200

@orders_bp.route('/queue', methods=['GET'])
@role_required(['chef'])
def get_chef_queue():
    """
    Returns all pending orders for the Chef's dashboard.
    """
    role = request.user.get('role')
    queue = OrderService.get_chef_queue(role)
    return jsonify([tx.to_dict() for tx in queue]), 200