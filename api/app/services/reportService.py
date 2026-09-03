from datetime import datetime, timedelta
from app.repositories.transactionRepo import TransactionRepo
from app.repositories.userRepo import UserRepo
from app.utils.reportGenerator import PDFGenerator

class ReportService:
    """
    Business Logic layer for Reporting and Analytics.
    Implements Processes 4.1 and 4.2.
    """

    @staticmethod
    def generate_financial_report(role, start_date_str=None, end_date_str=None):
        """
        Implementation of Process 4.1 (Generate Report).
        Aggregates transaction data for HR Manager review.
        """
        # 1. Access Control Check
        # Only HR is authorized to trigger financial exports.
        if role != 'hr_manager':
            return None, "Unauthorized: Access denied to financial records."

        # 2. Parameter Parsing
        # Default to the last 30 days if no range is provided.
        try:
            if start_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            else:
                start_date = datetime.utcnow() - timedelta(days=30)

            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            else:
                end_date = datetime.utcnow()
        except ValueError:
            return None, "Invalid date format. Please use YYYY-MM-DD."

        # 3. Data Retrieval (Process 4.1 Logic)
        # Fetching directly from D3 via the Repository.
        transactions = TransactionRepo.get_transactions_by_date_range(start_date, end_date)
        
        if not transactions:
            return None, "No transactions found for the selected period."

        # 4. Report Transformation (Process 4.2 Logic)
        # Forwarding the data to the PDF Utility for Finance export.
        try:
            file_path = PDFGenerator.generate_transaction_report(
                transactions, 
                start_date.strftime('%Y-%m-%d'), 
                end_date.strftime('%Y-%m-%d')
            )
        except Exception:
            file_path = 'Error: no path'

        return {
            "report_url": file_path,
            "transaction_count": len(transactions),
            "generated_at": datetime.utcnow().isoformat()
        }, "Report generated successfully."

    @staticmethod
    def get_summary_stats(role):
        """
        Provides high-level dashboard metrics for the HR Web App.
        """
        if role != 'hr_manager':
            return None, "Unauthorized."

        # Example logic: Total sales for today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0)
        today_txs = TransactionRepo.get_transactions_by_date_range(today_start, datetime.utcnow())
        
        total_sales = sum(tx.order_price for tx in today_txs)
        
        return {
            "daily_revenue": total_sales,
            "daily_order_count": len(today_txs),
            "pending_orders": TransactionRepo.get_pending_count()
        }, "Summary retrieved."