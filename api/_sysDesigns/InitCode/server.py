from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import functools

app = Flask(__name__)
app.secret_key = 'super_secret_production_key_here'

# Mock Database
mock_db = {
    'users': [
        {'id': 'CUST01', 'name': 'Alice Smith', 'email': 'alice@example.com', 'verified': True},
        {'id': 'CUST02', 'name': 'Bob Jones', 'email': 'bob@example.com', 'verified': False}
    ],
    'orders': [
        {'id': 'ORD01', 'customer': 'Alice Smith', 'item': 'Latte', 'date': '2026-08-11', 'amount': 4.50},
        {'id': 'ORD02', 'customer': 'Bob Jones', 'item': 'Muffin', 'date': '2026-08-11', 'amount': 3.00}
    ],
    'payments': [
        {'id': 'PAY01', 'date': '2026-08-10', 'amount': 150.00, 'status': 'Completed'}
    ]
}

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def root():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 2FA Trigger Logic
        session['pending_2fa'] = True
        return redirect(url_for('verify_2fa'))
    return render_template('login.html')

@app.route('/verify_2fa', methods=['GET', 'POST'])
def verify_2fa():
    if request.method == 'POST':
        # Assume valid 2FA token
        session.pop('pending_2fa', None)
        session['logged_in'] = True
        return redirect(url_for('analytics'))
    return render_template('2fa.html')

@app.route('/analytics')
@login_required
def analytics():
    return render_template('analytics.html')

@app.route('/users')
@login_required
def users():
    return render_template('users.html', users=mock_db['users'])

@app.route('/orders')
@login_required
def orders():
    return render_template('orders.html', orders=mock_db['orders'])

@app.route('/payments')
@login_required
def payments():
    return render_template('payments.html', payments=mock_db['payments'])

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/api/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)