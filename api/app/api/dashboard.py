import calendar
from functools import wraps
from pathlib import Path

from flask import Blueprint, render_template, redirect, request, session, url_for, jsonify, send_file

from app.services.reportService import ReportService
from app.security import role_required
from app.supabase_client import SupabaseStorage
from datetime import datetime

from app.models.user import User
from app.models.user import db
from app.models.payment import Payment
from app.models.menuItem import MenuItem
from app.models.Transaction import Transaction
from app.services.authService import AuthService
from app.utils.reportGenerator import PDFGenerator
# from app.repositories.paymentRepo import PaymentRepo


dashboard_bp = Blueprint('dashboard', __name__)



def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('dashboard.signin'))
        return view(*args, **kwargs)
    return wrapped


def _active_month_transactions(month=None):
    target_month = month or session.get('active_month')
    if not target_month:
        return []
    transactions = Transaction.query.order_by(Transaction.created_at.desc()).all()
    return [tx for tx in transactions if tx.created_at and tx.created_at.strftime('%Y-%m') == target_month]


def _payment_month_label(month_value):
    if not month_value:
        return ''
    year, month = month_value.split('-')
    year_num = int(year)
    month_num = int(month)
    last_day = calendar.monthrange(year_num, month_num)[1]
    return f"{month_value}-01 to {month_value}-{last_day}"


@dashboard_bp.route('/api/create/payment', methods=['POST'])
@admin_required
@role_required(['hr_manager'])
def pay():
    active_month = session.get('active_month')
    if not active_month:
        return jsonify({"status": "error", "message": "No active month selected."}), 400

    pending_orders = [
        tx for tx in _active_month_transactions(active_month)
        if tx.status == 'checked_out' and not tx.payment_id
    ]
    if not pending_orders:
        return jsonify({"status": "error", "message": "No unpaid checked out orders found for this month."}), 400

    total_price = round(sum(tx.order_price for tx in pending_orders), 2)
    payment = Payment(
        total_price=total_price,
        period=active_month,
        payment_status='unpaid',
        created_at=datetime.utcnow(),
    )
    from app.models.user import db
    db.session.add(payment)
    db.session.flush()

    for tx in pending_orders:
        tx.payment_id = payment.id
    db.session.commit()

    return jsonify({
        "status": "success",
        "payment_id": payment.id,
        "period": payment.period,
        "amount": float(payment.total_price),
        "orders_count": len(pending_orders),
        "message": "Payment batch created successfully."
    }), 201


@dashboard_bp.route('/api/payments/<int:payment_id>', methods=['GET'])
@admin_required
@role_required(['hr_manager'])
def get_payment_detail(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    transactions = Transaction.query.filter_by(payment_id=payment.id).order_by(Transaction.created_at.desc()).all()

    rows = []
    for tx in transactions:
        customer = User.query.get(tx.customer_id)
        item = MenuItem.query.get(tx.item_id)
        rows.append({
            'order_id': tx.id,
            'customer': customer.email if customer else 'Unknown Customer',
            'item': item.name,
            'date': tx.created_at.strftime('%Y-%m-%d') if tx.created_at else '',
            'amount': float(tx.order_price),
        })

    return jsonify({
        "status": "success",
        "payment": {
            "id": payment.id,
            "period": payment.period,
            "period_label": _payment_month_label(payment.period),
            "amount": float(payment.total_price),
            "status": payment.payment_status,
            "created_at": payment.created_at.strftime('%Y-%m-%d %H:%M:%S') if payment.created_at else '',
            "doc_url": payment.doc_url,
            "orders": rows,
        }
    })


@dashboard_bp.route('/api/payments/<int:payment_id>/mark-paid', methods=['POST'])
@admin_required
@role_required(['hr_manager'])
def mark_payment_paid(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    payment.payment_status = 'paid'
    payment.checked_out_at = datetime.utcnow()
    from app.models.user import db
    db.session.commit()
    return jsonify({"status": "success", "payment_id": payment.id, "status": payment.payment_status})


@dashboard_bp.route('/api/payments/<int:payment_id>/download', methods=['GET'])
@admin_required
@role_required(['hr_manager'])
def download_payment_document(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    output_format = (request.args.get('format') or 'pdf').lower()
    transactions = Transaction.query.filter_by(payment_id=payment.id).order_by(Transaction.created_at.desc()).all()
    rows = []
    for tx in transactions:
        customer = User.query.get(tx.customer_id)
        rows.append({
            'order_id': tx.id,
            'customer': customer.email if customer else 'Unknown Customer',
            'item': 'Cafe Order',
            'date': tx.created_at.strftime('%Y-%m-%d') if tx.created_at else '',
            'amount': float(tx.order_price),
        })
    file_path = PDFGenerator.generate_payment_export(payment, rows, output_format)
    payment.doc_url = file_path
    db.session.commit()

    mimetype_map = {
        'pdf': 'application/pdf',
        'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'csv': 'text/csv',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    }
    return send_file(file_path, as_attachment=True, download_name=Path(file_path).name, mimetype=mimetype_map.get(output_format, 'application/octet-stream'))


@dashboard_bp.route('/api/payments/<int:payment_id>/share', methods=['GET'])
@admin_required
@role_required(['hr_manager'])
def share_payment_document(payment_id):
    output_format = (request.args.get('format') or 'pdf').lower()
    share_url = url_for('dashboard.download_payment_document', payment_id=payment_id, format=output_format, _external=True)
    return jsonify({"status": "success", "format": output_format, "share_url": share_url})


@dashboard_bp.route('/api/get/active-month', methods=['POST'])
@admin_required
@role_required(['hr_manager'])
def month():
    data = request.get_json()
    active_monthizzo = data.get("month")

    if active_monthizzo :
        session["active_month"] = active_monthizzo
        #print(session["active_month"])
        return jsonify({"status": "success", "month": active_monthizzo})

    return jsonify({"status":"error", "message":"unable to update month"})


# endpoints for pages
@dashboard_bp.route('/', methods=['GET'])
def root():
    return redirect(url_for('dashboard.signin'))

@dashboard_bp.route('/signin', methods=['GET', 'POST'])
def signin():
    """
    endpoint for authorizing admin or HR
    """
    if request.method == 'POST':
        user_data = {
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            'employee_number': request.form.get('employee_id')
        }

        result, message = AuthService.login_user(user_data)
        if not result:
            return render_template('login.html', error=message), 401

        session.clear()
        session['admin_logged_in'] = True
        session['admin_user'] = result['user']
        session['admin_token'] = result['token']
        return redirect(url_for('dashboard.overview'))

    return render_template('login.html')


@dashboard_bp.route('/overview', methods=['GET'])
@admin_required
@role_required(['hr_manager'])
def overview():
    users = User.query.order_by(User.created_at.desc()).all()
    paymentz_unfiltered = Payment.query.order_by(Payment.created_at.desc()).all()
    transactionz_unfiltered = Transaction.query.order_by(Transaction.created_at.desc()).all()

    payments =  [ tx for tx in paymentz_unfiltered if tx.created_at.strftime('%Y-%m') == session["active_month"] ]
    transactions = [ tx for tx in transactionz_unfiltered if tx.created_at.strftime('%Y-%m') == session["active_month"] ]

    total_revenue = round(sum(p.total_price for p in payments), 2)
    pending_payments = sum(1 for p in payments if p.payment_status.lower() != 'paid')
    verified_users = sum(1 for user in users if user.is_verified)
    orders_cust_ids = {transaction.customer_id for transaction in transactions }
    users_in_orders = sum(1 for user in users if user.id in orders_cust_ids)
    total_orders = len(transactions)

    day_orders = {}
    days_in_a_month = {
        "01":31 ,"02":28 ,"03":31,"04":30 ,"05":30,"06":30, "07":31, "08":31,"09":30, "10":31,"11":30,"12":31
    }

    for month in days_in_a_month:
        #print(month)
        if month == session["active_month"][5:7]:
            for n in range(days_in_a_month[month] + 1):
                day_orders[str(n)] = 0

    #print(session["active_month"][5:7] )

    for tx in transactions:
        #print(day_orders)
        for m in days_in_a_month:
            #print(tx.created_at.strftime('%Y-%m')[5:7])
            if tx.created_at.strftime('%Y-%m')[5:7] == m:
                for dy in day_orders:
                    #print(dy, tx.created_at.strftime('%Y-%m-%d')[5:7])
                    if tx.created_at.strftime('%Y-%m-%d')[8:10] == dy:
                        day_orders[dy] += 1 
                    if tx.created_at.strftime('%Y-%m-%d')[8:9] == '0':
                        if tx.created_at.strftime('%Y-%m-%d')[9:10] == dy:
                            day_orders[dy] += 1 

    stats = {
        'total_revenue': total_revenue,
        'pending_payments': pending_payments,
        'verified_users': verified_users,
        'total_orders': total_orders,
        'recent_payments': payments[:5],
        'recent_users': users[:5],
        'users_orders_ratio' : str( (users_in_orders / verified_users ) * 100 ),
        'day_orders' : str([ day_orders[k] for k in day_orders]), 
        'order_status_counts': {
            'pending': sum(1 for t in transactions if t.status == 'pending'),
            'checked_out': sum(1 for t in transactions if t.status == 'checked_out'),
            'cancelled': sum(1 for t in transactions if t.status == 'cancelled')
        }
    }

    return render_template('pages/overview.html', stats=stats)


@dashboard_bp.route('/users', methods=['GET'])
@admin_required
@role_required(['hr_manager'])
def get_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('pages/users.html', users=[{
        'id': user.id,
        'name': user.email.split('@')[0].title(),
        'email': user.email,
        'verified': bool(user.is_verified),
        'employee_number': user.employee_number,
    } for user in users])


@dashboard_bp.route('/orders', methods=['GET'])
@admin_required
@role_required(['hr_manager'])
def get_orders():
    transactionz_unfiltered = Transaction.query.order_by(Transaction.created_at.desc()).all()
    transactions = [ tx for tx in transactionz_unfiltered if tx.created_at.strftime('%Y-%m') == session["active_month"] ]

    #price to be settled , for checked out orders
    total_price_amount = round(sum(tx.order_price for tx in transactions if tx.status == "checked_out"), 2)
    total_orders = sum(1 for tx in transactions if tx.status == "checked_out" )
    
    orders = []
    for tx in transactions:
        customer = User.query.get(tx.customer_id)
        item = MenuItem.query.get(tx.item_id)
        orders.append({
            'id': tx.id,
            'customer': customer.email if customer else 'Unknown Customer',
            'item': item.name,
            'date': tx.created_at.strftime('%Y-%m-%d') if tx.created_at else '',
            'paid': 'true' if tx.payment_id else '',
            'amount': float(tx.order_price),
            'status': tx.status,
        })
    return render_template(
        'pages/orders.html', 
        orders=orders, 
        total_price=total_price_amount, 
        total_orders=total_orders
    )


@dashboard_bp.route('/payments', methods=['GET'])
@admin_required
@role_required(['hr_manager'])
def get_payments():
    paymentz_unfiltered = Payment.query.order_by(Payment.created_at.desc()).all()
    payments =  [ tx for tx in paymentz_unfiltered if tx.created_at.strftime('%Y-%m') == session["active_month"] ]

    payment_rows = []
    for payment in payments:
        payment_rows.append({
            'id': payment.id,
            'date': payment.created_at.strftime('%Y-%m-%d') if payment.created_at else '',
            'amount': float(payment.total_price),
            'status': payment.payment_status,
            'period': str(payment.period),
            'orders_count': max(1, len(Transaction.query.filter_by(payment_id=payment.id).all())),
        })
    return render_template('pages/payments.html', payments=payment_rows)


@dashboard_bp.route('/profile', methods=['GET'])
@admin_required
@role_required(['hr_manager'])
def get_profile():
    user = session.get('admin_user') #or {'email': 'admin@msgcafe.com', 'employee_number': 'MSG27785'}
    return render_template('pages/user_profile1.html', user=user)


@dashboard_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('dashboard.signin'))

