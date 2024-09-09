import json
import os
from config import METADATA_FILE
import logging

logger = logging.getLogger(__name__)

def load_metadata():
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, 'r') as f:
                metadata = json.load(f)
            logger.info(f"Loaded metadata: {metadata}")
            return metadata
        except json.JSONDecodeError:
            logger.error("Error decoding metadata file. Starting with empty metadata.")
    else:
        logger.warning(f"Metadata file not found at {METADATA_FILE}")
    return {}

def save_metadata(metadata):
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f)
    logger.info(f"Saved metadata: {metadata}")