from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# to be imported by the main app.py
db = SQLAlchemy()

class User(db.Model):
    """
    D1: Users data store.
    Centralizes authentication and role-based access data.
    """
    __tablename__ = 'users'

    # Primary Identifier
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Authentication Credentials
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False) # Bcrypt hash
    
    # Identification for HR and Customers (Nullable for Chef as per DFD 1.1)
    employee_number = db.Column(db.String(50), unique=True, nullable=True)
    
    # Role-Based Access Control (RBAC)
    # Roles: 'customer', 'chef', 'hr_manager'
    role = db.Column(db.String(20), nullable=False)
    
    # Governance & Verification (DFD 1.3/1.4)
    # Initial registration sets this to False; HR must manually verify.
    is_verified = db.Column(db.Boolean, default=True, nullable=True)
    
    # Auditing Control
    # Essential for Audit to track account age and registration timing.
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.email} - Role: {self.role}>"

    def to_dict(self):
        """
        Helper for DFD 1.2: Returning Authenticated User Data.
        """
        return {
            "id": self.id,
            "email": self.email,
            "employee_number": self.employee_number,
            "role": self.role,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat()
        }