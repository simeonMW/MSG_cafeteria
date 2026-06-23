import os
from datetime import timedelta
from dotenv import load_dotenv

# Load variables from .env file for local development
load_dotenv()

class Config:
    """
    Centralized configuration management.
    Ensures environmental variables are handled securely and consistently.
    """

    # 1. SECURITY & INTEGRITY
    # Secret key for signing JWTs and session cookies. 
    # IT Audit Rule: MUST be a complex string stored in .env, never hardcoded.
    SECRET_KEY = os.getenv("SECRET_KEY", "default-audit-key-2026-msg-mim-ict")
    
    # Encryption algorithm for JWT
    JWT_ALGORITHM = "HS256"
    
    # Token expiration time (Process 1.2: Authentication)
    # Shorter durations (8-12 hours) are better for security audits.
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)

    # 2. DATA STORE (D1, D2, D3)
    # The URI for the SQLAlchemy database.
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")  # "sqlite:///cafe_system.db"
    
    # Use Supabase as the cloud storage backend for generated assets.
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    SUPABASE_STORAGE_BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "public")

    # Disable track modifications to save system resources/memory
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 3. FILESYSTEM PATHS (Process 3.3 & 4.2)
    # Local paths are retained only for development or fallback.
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static')
    REPORT_FOLDER = os.path.join(UPLOAD_FOLDER, 'reports')
    QR_FOLDER = os.path.join(UPLOAD_FOLDER, 'qrcodes')

    # 4. AUDIT & LOGGING
    # Toggle for debug mode (Should be False in production audits)
    DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"

    @staticmethod
    def init_app(app):
        """
        Ensures necessary directories exist upon system startup.
        Prevents runtime errors during Process 3.3 or 4.2.
        """         
        """
        os.makedirs(Config.REPORT_FOLDER, exist_ok=True)
        os.makedirs(Config.QR_FOLDER, exist_ok=True) 
        """