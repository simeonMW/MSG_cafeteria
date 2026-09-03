from datetime import datetime
from app.models.user import db

class Payment(db.Model):
    """
    Represents the D4: Payments data store.  // added entity after initial design
    The central ledger for all batch payments, and payment fulfillment statuses.
    """
    __tablename__ = 'payments'

    # Primary Identifier
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Relationships (Foreign Keys)
    # Linked to orders to be paid
    # customer_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    # oders_ids = db.Column(db.String(120), unique=True, nullable=False)

    # Financial Integrity
    total_price = db.Column(db.Float, nullable=False)

    # Auditing & Control
    # Precise timestamping for Process 4.0 (Reporting)
    period = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    checked_out_at = db.Column(db.DateTime, nullable=True) # Set when Admin/HR settles the payment

    # Fulfillment Status
    # payment statuses: 'paid', 'unpaid'
    payment_status = db.Column(db.String(20), default='unpaid', nullable=False)

    # payment document location
    doc_url = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<Payment {self.id} - Status: {self.payment_status} - For: {self.period}>"

    def to_dict(self):
        """
        Formats payment data for HR displays and reporting.
        """
        return {
            "payment_id": self.id,
            "total_price": self.total_price,
            "period": self.period,
            "payment_status": self.payment_status,
            "created_at": self.created_at.isoformat(),# if self.created_at else None,
            "checked_out_at": self.checked_out_at.isoformat() if self.checked_out_at else None,
            "doc_url": self.doc_url if self.doc_url else None,
        }


