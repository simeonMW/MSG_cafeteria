from fpdf import FPDF
from datetime import datetime
import os

class PDFGenerator:
    """
    Utility class for Process 4.2.
    Generates professional, auditable PDF reports for HR and Finance.
    """

    @staticmethod
    def generate_transaction_report(transactions, start_date, end_date):
        """
        Creates a PDF summary of all transactions within a specific range.
        Includes headers, detailed tables, and total revenue calculation.
        """
        pdf = FPDF()
        pdf.add_page()
        
        # 1. Header & Title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Automated Cafe Ordering System - Financial Report", ln=True, align='C')
        
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Reporting Period: {start_date} to {end_date}", ln=True, align='C')
        pdf.cell(0, 10, f"Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC", ln=True, align='C')
        pdf.ln(10)

        # 2. Table Headers
        # Defined widths for columns to ensure data alignment (Auditable layout)
        pdf.set_font("Arial", 'B', 10)
        pdf.set_fill_color(200, 220, 255) # Light blue background for header
        pdf.cell(30, 10, "ID", 1, 0, 'C', True)
        pdf.cell(60, 10, "Order Date", 1, 0, 'C', True)
        pdf.cell(60, 10, "Customer ID", 1, 0, 'C', True)
        pdf.cell(40, 10, "Amount (MWK)", 1, 1, 'C', True)

        # 3. Data Rows
        pdf.set_font("Arial", '', 10)
        total_revenue = 0
        
        for tx in transactions:
            pdf.cell(30, 8, str(tx.id), 1, 0, 'C')
            pdf.cell(60, 8, tx.created_at.strftime('%Y-%m-%d %H:%M'), 1, 0, 'C')
            pdf.cell(60, 8, str(tx.customer_id), 1, 0, 'C')
            pdf.cell(40, 8, f"{tx.order_price:,.2f}", 1, 1, 'R')
            total_revenue += tx.order_price

        # 4. Footer & Summary
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(150, 10, "Total Gross Revenue:", 0, 0, 'R')
        pdf.cell(40, 10, f"{total_revenue:,.2f}", 1, 1, 'R')

        # 5. Output Management
        directory = "app/static/reports"
        if not os.path.exists(directory):
            os.makedirs(directory)

        file_name = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = os.path.join(directory, file_name)
        
        pdf.output(file_path)
        
        return file_path