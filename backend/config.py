import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", str(BASE_DIR / "uploads"))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 50 * 1024 * 1024))
    JSON_SORT_KEYS = False
    TESTING = False
    DEBUG = False
    
    # SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "pool_recycle": 3600,
        "pool_pre_ping": True,
    }
    
    # Configuración de archivos
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'mp3', 'mp4', 'wav', 'avi', 'sql', 'py', 'js', 'json', 'xml', 'csv', 'yaml', 'yml', 'md', 'html', 'css', 'java', 'cpp', 'c', 'h', 'zip', 'tar', 'gz', 'dll', 'exe', 'bin', 'db', 'sqlite', 'sqlite3'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
