import json
import os
from typing import Dict, Any
from ..config import METADATA_FILE, CLIENT_DB_FILE
import logging

logger = logging.getLogger(__name__)

def load_metadata() -> Dict[str, Any]:
    """
    Loads metadata from the metadata.json file.
    Ensures that the 'pdfs' key exists and moves any misplaced PDF entries to it.

    Returns:
        Dict[str, Any]: A dictionary containing the metadata.
    """
    logger.info(f"Attempting to load metadata from {METADATA_FILE}")
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, 'r') as f:
                metadata = json.load(f)
            # Ensure 'pdfs' key exists in metadata
            if 'pdfs' not in metadata:
                metadata['pdfs'] = {}
            # Move any misplaced PDF entries to the 'pdfs' key
            for key, value in list(metadata.items()):
                if key != 'pdfs' and isinstance(value, dict) and 'publication_name' in value:
                    metadata['pdfs'][key] = value
                    del metadata[key]
            logger.info(f"Loaded metadata with {len(metadata['pdfs'])} PDFs")
            return metadata
        except json.JSONDecodeError:
            logger.error("Error decoding metadata file. Starting with empty metadata.")
    else:
        logger.warning(f"Metadata file not found at {METADATA_FILE}")
    return {'pdfs': {}}

def save_metadata(metadata: Dict[str, Any]) -> None:
    """
    Saves metadata to the metadata.json file.

    Args:
        metadata (Dict[str, Any]): The metadata to be saved.
    """
    logger.info(f"Saving metadata with {len(metadata['pdfs'])} PDFs")
    os.makedirs(os.path.dirname(METADATA_FILE), exist_ok=True)
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Metadata saved to {METADATA_FILE}")

def get_pdf_count() -> int:
    """
    Returns the total number of PDFs in metadata.

    Returns:
        int: The count of PDFs in the metadata.
    """
    metadata = load_metadata()
    count = len(metadata['pdfs'])
    logger.info(f"PDF count: {count}")
    return count

def load_clients() -> Dict[str, Any]:
    """
    Loads clients from the client_database.json file.

    Returns:
        Dict[str, Any]: A dictionary containing client data.
    """
    logger.info(f"Loading clients from {CLIENT_DB_FILE}")
    if os.path.exists(CLIENT_DB_FILE):
        with open(CLIENT_DB_FILE, 'r') as f:
            clients = json.load(f)
        return clients
    else:
        logger.warning(f"Client database file not found at {CLIENT_DB_FILE}")
        return {}