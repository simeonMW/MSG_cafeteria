import os
from datetime import timedelta
from dotenv import load_dotenv
from sqlalchemy.pool import NullPool

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
    # Shorter durations are better for security.
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)

    # 2. DATA STORE (D1, D2, D3) // D4 added for batch payments     ## are switched off for dev env
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME")

    DATABASE_URL = os.getenv("DATABASE_URL")

    if os.getenv("FLASK_ENV") == "production":
        if DATABASE_URL:
            if DATABASE_URL.startswith("postgresql://"):
                SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
            else:
                SQLALCHEMY_DATABASE_URI = DATABASE_URL
        elif DB_USER and DB_PASSWORD and DB_HOST and DB_NAME:
            SQLALCHEMY_DATABASE_URI = (
                f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
                "?sslmode=require"
            )
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///cafe_system.db"

    SQLALCHEMY_ENGINE_OPTIONS = {
        "poolclass": NullPool,
        "pool_pre_ping": True
        #"connect_args": {"sslmode": "require"},
    }

    # cloud storage backend for generated assets. (Supabase)
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    SUPABASE_STORAGE_BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "public")

    # Disable track modifications to save system resources/memory
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 3. FILESYSTEM PATHS (Process 3.3 & 4.2)
    # Local paths are retained only for development or fallback.

    """ 
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static')
    REPORT_FOLDER = os.path.join(UPLOAD_FOLDER, 'reports')
    QR_FOLDER = os.path.join(UPLOAD_FOLDER, 'qrcodes') 
    """

    # 4. LOGGING
    # Toggle for debug mode (False in production audits)
    DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"
    ENV = os.getenv("FLASK_ENV")

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