from flask import Blueprint, request, jsonify, send_file
from app.services.reportService import ReportService
from app.security import role_required
import os

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/generate', methods=['POST'])
@role_required(['hr_manager'])
def generate_report():
    """
    Endpoint for Process 4.1 & 4.2.
    Aggregates D3 data and generates a PDF for Finance.
    """
    data = request.get_json() or {}
    role = request.user.get('role')
    
    # Optional date filters from the HR Web App
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    result, msg = ReportService.generate_financial_report(role, start_date, end_date)
    
    if not result:
        return jsonify({"error": msg}), 400

    return jsonify({
        "message": msg,
        "report_details": result
    }), 200

@reports_bp.route('/download', methods=['GET'])
@role_required(['hr_manager'])
def download_report():
    """
    Endpoint to physically retrieve the generated PDF file.
    """
    file_path = request.args.get('path')
    
    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "Report file not found"}), 404

    # Security Check: Ensure the user isn't trying to access files outside the reports directory
    if not file_path.startswith("app/static/reports"):
        return jsonify({"error": "Unauthorized file access"}), 403

    return send_file(file_path, as_attachment=True)

@reports_bp.route('/summary', methods=['GET'])
@role_required(['hr_manager'])
def get_dashboard_summary():
    """
    Provides real-time metrics for the HR Manager's dashboard.
    """
    role = request.user.get('role')
    result, msg = ReportService.get_summary_stats(role)
    
    if not result:
        return jsonify({"error": msg}), 403
        
    return jsonify(result), 200