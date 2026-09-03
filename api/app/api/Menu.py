import os
from flask import Blueprint, request, jsonify
from app.services.menuService import MenuService
from app.security import role_required
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load variables from .env file for local development
load_dotenv()

def save_image(file):
    base_dir = os.getenv('UPLOAD_FOLDER', 'app/static/menu')
    filename = secure_filename(file.filename)

    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    system_path = os.path.join(base_dir, filename)

    file.save(system_path)

    return system_path


menu_bp = Blueprint('menu', __name__)


@menu_bp.route('/public', methods=['GET'])
@role_required(['customer', 'chef', 'hr_manager'])
def get_menu():
    """
    Endpoint for Process 3.1: Fetch Menu.
    Returns items that are currently marked as available.
    """
    menu_items = MenuService.get_public_menu()
    return jsonify(menu_items), 200

@menu_bp.route('/inventory', methods=['GET'])
@role_required(['chef'])
def get_inventory():
    """
    Chef-only endpoint to see all items, including out-of-stock items.
    """
    role = request.user.get('role')
    items, error = MenuService.get_full_inventory(role)
    
    
    if error:
        return jsonify({"error": error}), 403
    return jsonify(items), 200


@menu_bp.route('/add', methods=['POST'])
@role_required(['chef'])
def add_item():
    """
    Endpoint for Process 2.1: Menu Entry.
    Allows the Chef to add new resources to D2.
    """
    #menu_item_image = request.files['picture_url']
    #menu_item_image_url = save_image(menu_item_image)
    data = request.get_json()
    """ data = {
        'name' : request.form['name'],
        'description' : request.form['description'],
        'price' : request.form['price'],
        'picture_url' : save_image(request.files['image'])
    } """
    #data.picture_url = menu_item_image_url
    #print(data)
    role = request.user.get('role')
    
    # Basic Input Validation
    if not data.get('name') or not data.get('price'):
        return jsonify({"error": "Name and Price are required"}), 400

    result, msg = MenuService.add_item(data, role)
    if not result:
        return jsonify({"error": msg}), 403

    return jsonify({"message": msg, "item": result}), 201

@menu_bp.route('/update/<int:item_id>', methods=['PUT'])
@role_required(['chef'])
def update_item(item_id):
    """
    Endpoint for Process 2.2: Menu Update.
    Allows the Chef to modify existing item details or prices.
    """
    data = request.get_json()
    role = request.user.get('role')
    
    result, msg = MenuService.update_item_details(item_id, data, role)
    if not result:
        return jsonify({"error": msg}), 404

    return jsonify({"message": msg, "item": result}), 200

@menu_bp.route('/toggle/<int:item_id>', methods=['PATCH'])
@role_required(['chef'])
def toggle_item(item_id):
    """
    Quick toggle for availability status.
    """
    role = request.user.get('role')
    result, msg = MenuService.toggle_item_status(item_id, role)
    
    if not result:
        return jsonify({"error": msg}), 404
        
    return jsonify({"message": msg, "data": result}), 200