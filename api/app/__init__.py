from flask import Flask, jsonify, session
from flask_migrate import Migrate
from app.config import Config
from app.models.user import db
from datetime import datetime

def create_app(config_class=Config):
    """
    Application Factory Pattern.
    maintainable
    easy testing
    auditing of the configuration state.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    #production or development
    if app.config['ENV'] == "production":
        migration_directory = "migrations"
    else:
        migration_directory = "migrations_dev"

    # Initialize Configuration (creates necessary directories)
    #Config.init_app(app)

    # 1. Initialize Database with the Flask App
    db.init_app(app)

    # 2. Initialize Flask-Migrate
    # This handles Process Change Management for D1, D2, D3, and D4
    Migrate(app, db, directory=migration_directory)

    # Import blueprints here to avoid circular imports
    from app.api.Auth import auth_bp
    from app.api.Menu import menu_bp
    from app.api.orders import orders_bp
    from app.api.reports import reports_bp
    from app.api.cronJob import health_bp
    from app.api.dashboard import dashboard_bp

    # REGISTER BLUEPRINTS (Process Segregation)
    
    # Process 1.0: User Management & Authentication
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # Process 2.0: Menu Management (Chef Actions)
    app.register_blueprint(menu_bp, url_prefix='/api/menu')
    
    # Process 3.0: Ordering & Validation (Customer & Chef)
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    
    # Process 4.0: Reporting & Finance Exports (HR)
    app.register_blueprint(reports_bp, url_prefix='/api/reports')

    # dashboard endpoints (HR)
    app.register_blueprint(dashboard_bp, url_prefix='/admin')
    
    # redundantProcess: Health Check & Cron Jobs
    app.register_blueprint(health_bp, url_prefix='/api/health')

    # selects a month b4 first admin request
    @app.before_request
    def set_month():
        #print(session["active_month"])
        if "active_month" not in session:
            session["active_month"] = datetime.now().strftime('%Y-%m')
            #print(session["active_month"])

    #selects an active month , its global for all pages of admin
    @app.context_processor
    def active_month():
        return {"active_month": session.get("active_month")}

    # error handlers (for Log Consistency)
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        # In production, the traceback logs for D3 reconciliation
        return jsonify({"error": "Internal server error. Contact system admin."}), 500

    return app
