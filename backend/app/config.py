# backend/app/config.py

import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Root directory (parent of backend)
ROOT_DIR = Path(__file__).resolve().parent.parent

# Data directory
DATA_DIR = ROOT_DIR / "DATA"

# Upload directory
UPLOAD_DIR = DATA_DIR / "uploaded_pdfs"

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Metadata file path
METADATA_FILE = DATA_DIR / "metadata.json"

# Client database file path
CLIENT_DB_FILE = DATA_DIR / "client_database.json"

# Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOGGING_CONFIG = {
    "version": 1,  # This key is mandatory
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(lineno)d %(message)s"
        },
    },
    "handlers": {
        "console": {
            "level": LOG_LEVEL,
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "level": LOG_LEVEL,
            "formatter": "json",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(DATA_DIR / "app.log"),  # Convert Path to string
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["console", "file"],
            "level": LOG_LEVEL,
            "propagate": True
        }
    }
}

# PDF extraction zoom level
PDF_EXTRACTION_ZOOM = 2.0

# Rate limiting configurations for the first model
BATCH_SIZE = 15  # For gemini-1.5-flash
RATE_LIMIT_INTERVAL = 60  # In seconds

# Rate limiting configurations for the second model
BATCH_SIZE_PRO = 2  # For gemini-1.5-pro-latest
RATE_LIMIT_INTERVAL_PRO = 60  # In seconds

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/newspaper_reader")
