from datetime import datetime
from app.models.Transaction import Transaction, db
from sqlalchemy import and_

class TransactionRepo:
    """
    Data Access Layer for D3: Transactions.
    Maintains the integrity of order logs, tokens, and fulfillment states.
    """

    @staticmethod
    def create(customer_id, item_id, snapshot_price, token, qr_path):
        """
        Implementation of DFD 3.2 & 3.3.
        Persists the order and the generated token/QR data to D3.
        """
        new_tx = Transaction(
            customer_id=customer_id,
            item_id=item_id,
            order_price=snapshot_price, # Crucial for Audit: Snapshotted at time of sale
            token=token,
            qr_code_path=qr_path,
            status='pending',
            created_at=datetime.utcnow()
        )
        db.session.add(new_tx)
        db.session.commit()
        return new_tx

    @staticmethod
    def get_by_token(token_str):
        """
        Implementation of DFD 3.4 (Validate Process).
        Used by the Chef to find the specific record associated with a scanned QR.
        """
        return Transaction.query.filter_by(token=token_str).first()

    @staticmethod
    def mark_as_checked_out(tx_id):
        """
        Finalizes the transaction loop.
        Updates status and records the timestamp for fulfillment auditing.
        """
        tx = Transaction.query.get(tx_id)
        if tx:
            tx.status = 'checked_out'
            tx.checked_out_at = datetime.utcnow()
            db.session.commit()
            return tx
        return None

    @staticmethod
    def get_user_history(customer_id):
        """
        Retrieves all transactions for a specific customer.
        Used to populate the 'My Orders' section of the Mobile App.
        """
        return Transaction.query.filter_by(customer_id=customer_id)\
            .order_by(Transaction.created_at.desc()).all()

    @staticmethod
    def get_transactions_by_date_range(start_date, end_date):
        """
        Implementation of DFD 4.1 (Generate Report Process).
        Retrieves data for HR and Finance audits within a specific window.
        """
        return Transaction.query.filter(
            and_(
                Transaction.created_at >= start_date,
                Transaction.created_at <= end_date
            )
        ).all()

    @staticmethod
    def get_pending_count():
        """
        Operational metric for the Chef app to show how many orders 
        are currently in the queue.
        """
        return Transaction.query.filter_by(status='pending').count()