# backend/app/utils/file_utils.py

import os
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

def save_image(image, path, format="PNG", quality=95):
    try:
        image.save(path, format=format, quality=quality)
        logger.info(f"Image saved at {path}")
    except Exception as e:
        logger.error(f"Failed to save image at {path}: {str(e)}")
        raise e

def load_image(path):
    try:
        with Image.open(path) as img:
            return img.convert('RGB')
    except Exception as e:
        logger.error(f"Failed to load image from {path}: {str(e)}")
        raise e

def read_file_bytes(path):
    try:
        with open(path, 'rb') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read file from {path}: {str(e)}")
        raise e
