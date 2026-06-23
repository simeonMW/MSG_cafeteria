from app.repositories.transactionRepo import TransactionRepo
from app.repositories.menuRepo import MenuRepo
from app.utils.qrTokenGenerator import QRGen
from datetime import datetime


class OrderService:
    """
    Business Logic layer for Transactions.
    Implements Processes 3.2, 3.3, and 3.4.
    """

    @staticmethod
    def place_order(user_id, item_id):
        """
        Implementation of Process 3.2 & 3.3.
        Orchestrates order placement, price snapshotting, and token generation.
        """
        # 1. Fetch Item from D2 (Process 3.2 Logic)
        item = MenuRepo.get_by_id(item_id)
        if not item or not item.is_available:
            return None, "Item is currently unavailable or does not exist."

        # 2. Generate Unique Token & QR (Process 3.3 Logic)
        token = QRGen.generate_secure_token()
        qr_path = QRGen.create_qr_image(token)

        # 3. Persist to D3 (Transaction Ledger)
        # Snapshotting the price here ensures audit integrity.
        transaction = TransactionRepo.create(
            customer_id=user_id,
            item_id=item_id,
            snapshot_price=item.price,
            token=token,
            qr_path=qr_path
        )

        return transaction, "Order placed successfully. QR Code generated."

    @staticmethod
    def validate_fulfillment(token_str, role):
        """
        Implementation of Process 3.4 (Validate).
        Used by the Chef to finalize the transaction.
        """
        # Audit Check: Only the Chef can fulfill orders
        if role != 'chef':
            return False, "Unauthorized: Only the Chef can verify tokens."

        # Fetch from D3 using the unique token index
        transaction = TransactionRepo.get_by_token(token_str)
    
        if not transaction:
            return False, "Invalid Token: No matching transaction found."

        if transaction.status == 'checked_out':
            return False, "Security Alert: This token has already been used."

        # Finalize the transaction
        TransactionRepo.mark_as_checked_out(transaction.id)
    
        return True, f"Success: Order #{transaction.id} verified and fulfilled."

    @staticmethod
    def get_customer_history(user_id):
        """
        Logic for the Customer Mobile App to view personal order logs.
        """
        return TransactionRepo.get_user_history(user_id)

    @staticmethod
    def get_transaction_by_id(tx_id):
        """
        Fetch a single transaction by its id.
        This is used when generating signed URLs for customer assets.
        """
        return TransactionRepo.get_by_id(tx_id)

    @staticmethod
    def get_chef_queue(role):
        """
        Logic for the Chef Mobile App to see active (pending) orders.
        """
        if role != 'chef':
            return None, "Unauthorized."
        
        # We filter for pending only to keep the Chef's UI clean
        all_tx = TransactionRepo.get_transactions_by_date_range(
            start_date=datetime.utcnow().replace(hour=0, minute=0, second=0),
            end_date=datetime.utcnow()
        )
        return [tx for tx in all_tx if tx.status == 'pending']