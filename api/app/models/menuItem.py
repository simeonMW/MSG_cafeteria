from datetime import datetime
from app.models.user import db

class MenuItem(db.Model):
    """
    Represents the D2: Menu data store.
    Contains the offerings managed by the Chef and displayed to Customers.
    """
    __tablename__ = 'menu_items'

    # Primary Identifier
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Item Details
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    
    # Financial Data
    # Use Numeric/Decimal for currency to avoid floating-point errors in audits
    price = db.Column(db.Float, nullable=False) 
    
    # Media & Display
    picture_url = db.Column(db.String(255), nullable=True)
    
    # Operational Status
    # Allows the Chef to "remove" an item from the menu without deleting the record,
    # preserving referential integrity for old transactions.
    is_available = db.Column(db.Boolean, default=True, nullable=False)

    # Auditing & Control
    # Tracks when the Chef (Process 2.1) last modified the item details or price.
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship back-reference (Optional but helpful for ORM navigation)
    # This links to the Transaction model we will define next.
    transactions = db.relationship('Transaction', backref='menu_item', lazy=True)

    def __repr__(self):
        return f"<MenuItem {self.name} - K{self.price}>"

    def to_dict(self):
        """
        Formats data for Process 3.1 (Fetch Menu).
        Provides a clean JSON-ready dictionary for the mobile apps.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "picture_url": self.picture_url,
            "is_available": self.is_available,
            "updated_at": self.updated_at.isoformat()
        }