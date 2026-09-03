from datetime import datetime
from app.models.payment import Payment, db
from sqlalchemy import and_


class PaymentRepo:
    """
    Data Access Layer for D4: Payments.
    Maintains the integrity of payment logs, and fulfillment states.
    """
    @staticmethod
    def create(total_price,period):
        """
        Implementation of DFD 3.2 & 3.3.
        Persists the order and the generated token/QR data to D3.
        """
        new_tx = Payment(
            total_price=total_price,
            period=period,
            payment_status='unpaid',
            created_at=datetime.utcnow()
        )
        db.session.add(new_tx)
        db.session.commit()
        return new_tx


    @staticmethod
    def get_payments_by_date_range(start_date, end_date):
        """
        Retrieves data for admin/HR
        """
        return Payment.query.filter(
            and_(
                Payment.created_at >= start_date,
                Payment.created_at <= end_date
            )
        ).all()

    @staticmethod
    def get_by_id(tx_id):
        """
        Fetch a Payment by its primary key.
        Used for secure HR access to pament record.
        """
        return Payment.query.get(tx_id)

    @staticmethod
    def get_unpaid_count():
        """
        Operational metric for the admin/HR to show how many Payments
        are currently in the queue.
        """
        return Payment.query.filter_by(status='unpaid').count()