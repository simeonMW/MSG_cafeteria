import os
import random
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'msg-cafe-admin-secret-key-2026')

# ==============================================================================
# Mock Databases & Persistent In-Memory State
# ==============================================================================

MOCK_ADMIN_CREDENTIALS = {
    'employee_id': 'msg27785',
    'email': 'admin@gmail.com',
    'password': 'password123',
    'name': 'Cafe Admin User',
    'role': 'Super Administrator'
}

MOCK_USERS = [
    {'id': 'USR-101', 'name': 'John Doe', 'email': 'john@example.com', 'department': 'Kitchen', 'verified': True},
    {'id': 'USR-102', 'name': 'Jane Smith', 'email': 'jane@example.com', 'department': 'Service', 'verified': True},
    {'id': 'USR-103', 'name': 'Robert Johnson', 'email': 'robert@example.com', 'department': 'Inventory', 'verified': False},
    {'id': 'USR-104', 'name': 'Emily Davis', 'email': 'emily@example.com', 'department': 'Management', 'verified': True},
    {'id': 'USR-105', 'name': 'Michael Brown', 'email': 'michael@example.com', 'department': 'Service', 'verified': False},
]

MOCK_PAYMENTS = {
    'PAY-9901': {
        'id': 'PAY-9901',
        'customer': 'Kitchen Operations',
        'amount': 1245.50,
        'status': 'completed',
        'reporting_period': '2026-08-01 to 2026-08-15',
        'generated_at': '2026-08-15 14:30:00 UTC',
        'orders': [
            {'id': 'ORD-501', 'customer': 'Kitchen Crew', 'item': 'Espresso Beans (5kg)', 'qty': 4, 'date': '2026-08-10', 'amount': 450.00},
            {'id': 'ORD-502', 'customer': 'Kitchen Crew', 'item': 'Oat Milk Crates', 'qty': 10, 'date': '2026-08-12', 'amount': 320.00},
            {'id': 'ORD-503', 'customer': 'Kitchen Crew', 'item': 'Pastry Stock', 'qty': 15, 'date': '2026-08-14', 'amount': 475.50}
        ]
    },
    'PAY-9902': {
        'id': 'PAY-9902',
        'customer': 'Front Desk Cafe',
        'amount': 890.00,
        'status': 'pending',
        'reporting_period': '2026-08-16 to 2026-08-31',
        'generated_at': '2026-08-20 09:15:00 UTC',
        'orders': [
            {'id': 'ORD-510', 'customer': 'Front Desk', 'item': 'Takeout Cups & Lids', 'qty': 20, 'date': '2026-08-18', 'amount': 500.00},
            {'id': 'ORD-511', 'customer': 'Front Desk', 'item': 'Syrup Supplies', 'qty': 8, 'date': '2026-08-19', 'amount': 390.00}
        ]
    },
    'PAY-9903': {
        'id': 'PAY-9903',
        'customer': 'Event Catering',
        'amount': 2100.75,
        'status': 'completed',
        'reporting_period': '2026-08-01 to 2026-08-31',
        'generated_at': '2026-08-22 11:45:00 UTC',
        'orders': [
            {'id': 'ORD-520', 'customer': 'Corporate Event A', 'item': 'Catering Package Heavy', 'qty': 1, 'date': '2026-08-21', 'amount': 2100.75}
        ]
    }
}


# ==============================================================================
# Helper Decorator for Authentication Protection
# ==============================================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ==============================================================================
# Authentication & 2FA Flow Routes
# ==============================================================================

@app.route('/login', methods=['GET'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('analytics'))
    return render_template('login.html')


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    emp_id = data.get('employee_id', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if (emp_id == MOCK_ADMIN_CREDENTIALS['employee_id'] and
        email == MOCK_ADMIN_CREDENTIALS['email'] and
        password == MOCK_ADMIN_CREDENTIALS['password']):
        
        session['pending_2fa'] = True
        session['2fa_email'] = email
        session['2fa_code'] = '849201'  # Default test 2FA OTP
        
        return jsonify({
            'success': True,
            'message': 'Credentials verified. 2FA required.',
            'redirect': url_for('verify_2fa')
        })

    return jsonify({
        'success': False,
        'message': 'Invalid Employee ID, Email, or Password combination.'
    }), 401


@app.route('/verify-2fa', methods=['GET'])
def verify_2fa():
    if not session.get('pending_2fa'):
        return redirect(url_for('login'))
    if session.get('logged_in'):
        return redirect(url_for('analytics'))
    return render_template('2fa.html')


@app.route('/api/verify-2fa', methods=['POST'])
def api_verify_2fa():
    if not session.get('pending_2fa'):
        return jsonify({'success': False, 'message': 'Session expired. Please log in again.'}), 403

    data = request.get_json() or {}
    entered_code = data.get('code', '').strip()
    expected_code = session.get('2fa_code', '849201')

    if entered_code == expected_code or entered_code == '123456':
        session.pop('pending_2fa', None)
        session.pop('2fa_code', None)
        session['logged_in'] = True
        session['admin_user'] = MOCK_ADMIN_CREDENTIALS['employee_id']

        return jsonify({
            'success': True,
            'message': 'Verification successful!',
            'redirect': url_for('analytics')
        })

    return jsonify({
        'success': False,
        'message': 'Invalid 2FA code. Please enter valid code (Test: 849201).'
    }), 400


@app.route('/api/resend-2fa', methods=['POST'])
def api_resend_2fa():
    if not session.get('pending_2fa'):
        return jsonify({'success': False, 'message': 'Invalid authentication session.'}), 403

    new_code = str(random.randint(100000, 999999))
    session['2fa_code'] = new_code

    return jsonify({
        'success': True,
        'message': f'New verification code dispatched to {session.get("2fa_email")}. (Test code: {new_code})'
    })


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ==============================================================================
# Dashboard Main Pages Routes
# ==============================================================================

@app.route('/')
@app.route('/analytics')
@login_required
def analytics():
    stats = {
        'total_orders': 1248,
        'placed_orders': 848,
        'no_orders': 400,
        'active_users': 156
    }
    return render_template('analytics.html', stats=stats)


@app.route('/users')
@login_required
def user_management():
    return render_template('users.html', users=MOCK_USERS)


@app.route('/orders')
@login_required
def orders():
    return render_template('orders.html')


@app.route('/payments')
@login_required
def payments():
    return render_template('payments.html', payments=list(MOCK_PAYMENTS.values()))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', admin=MOCK_ADMIN_CREDENTIALS)


# ==============================================================================
# Dynamic Backend API Endpoints (User Toggle, Payments Detail, Profile Update)
# ==============================================================================

@app.route('/api/users/<user_id>/toggle-verify', methods=['POST'])
@login_required
def toggle_user_verification(user_id):
    data = request.get_json() or {}
    is_verified = data.get('verified', False)

    for user in MOCK_USERS:
        if user['id'] == user_id:
            user['verified'] = is_verified
            return jsonify({
                'success': True,
                'message': f"User {user_id} verification set to {is_verified}",
                'user': user
            })

    return jsonify({'success': False, 'message': 'User not found'}), 404


@app.route('/api/payments/<payment_id>', methods=['GET'])
@login_required
def get_payment_details(payment_id):
    payment = MOCK_PAYMENTS.get(payment_id)
    if payment:
        return jsonify({'success': True, 'payment': payment})
    return jsonify({'success': False, 'message': 'Payment record not found'}), 404


@app.route('/api/profile/update', methods=['POST'])
@login_required
def update_profile_field():
    data = request.get_json() or {}
    field = data.get('field')
    value = data.get('value', '').strip()

    if field in MOCK_ADMIN_CREDENTIALS and value:
        MOCK_ADMIN_CREDENTIALS[field] = value
        return jsonify({
            'success': True,
            'message': f"Field '{field}' updated successfully.",
            'field': field,
            'value': value
        })

    return jsonify({'success': False, 'message': 'Invalid update request.'}), 400


# ==============================================================================
# Server Execution Block
# ==============================================================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)