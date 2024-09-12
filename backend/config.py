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
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": LOG_LEVEL,
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["default"],
            "level": LOG_LEVEL,
            "propagate": True
        }
    }
}

# Add this to your existing config.py
PDF_EXTRACTION_ZOOM = 2.0