from datetime import datetime
from app.models.user import db

class Transaction(db.Model):
    """
    Represents the D3: Transactions data store.
    The central ledger for all orders, tokens, and fulfillment statuses.
    """
    __tablename__ = 'transactions'

    # Primary Identifier
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Relationships (Foreign Keys)
    # Linked to User (Customer) and MenuItem
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)
    
    # Financial Audit Integrity
    # We store the price at the moment of the transaction to prevent 
    # historical data corruption if the Menu price is updated later.
    order_price = db.Column(db.Float, nullable=False)
    
    # Process 3.3: Token & QR Data
    # The token is unique and indexed for fast lookup during Chef validation.
    token = db.Column(db.String(100), unique=True, nullable=True, index=True)
    qr_code_path = db.Column(db.String(255), nullable=True) # Path to generated image
    
    # Process 3.4: Fulfillment Status
    # Statuses: 'pending', 'checked_out', 'cancelled'
    status = db.Column(db.String(20), default='pending', nullable=False)
    
    # Auditing & Control
    # Precise timestamping for Process 4.0 (Reporting)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    checked_out_at = db.Column(db.DateTime, nullable=True) # Set when Chef validates

    def __repr__(self):
        return f"<Transaction {self.id} - Status: {self.status} - Token: {self.token}>"

    def to_dict(self):
        """
        Formats transaction data for Customer and HR displays.
        Includes customer and item details through SQLAlchemy back-references.
        """
        return {
            "transaction_id": self.id,
            "customer_id": self.customer_id,
            "item_id": self.item_id,
            "amount": self.order_price,
            "token": self.token,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "checked_out_at": self.checked_at.isoformat() if self.checked_out_at else None
        }