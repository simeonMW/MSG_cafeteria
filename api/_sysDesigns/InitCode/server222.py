@app.route('/api/users', methods=['GET'])
@login_required
def get_users():
    return jsonify({'success': True, 'users': mock_db['users']})

@app.route('/api/users/<user_id>/toggle-verify', methods=['POST'])
@login_required
def toggle_user_verification(user_id):
    data = request.get_json() or {}
    is_verified = data.get('verified', False)
    
    # Locate user in mock database
    user = next((u for u in mock_db['users'] if u['id'] == user_id), None)
    if user:
        user['verified'] = is_verified
        return jsonify({
            'success': True, 
            'message': f"User {user_id} verification set to {is_verified}",
            'user': user
        })
    
    return jsonify({'success': False, 'message': 'User not found'}), 404