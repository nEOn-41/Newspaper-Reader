import os
from PIL import Image
import logging
from typing import Union

logger = logging.getLogger(__name__)

def save_image(image: Image.Image, path: Union[str, os.PathLike], format: str = "PNG", quality: int = 95) -> None:
    """
    Saves an image to the specified path.

    Args:
        image (Image.Image): The PIL Image object to be saved.
        path (Union[str, os.PathLike]): The path where the image should be saved.
        format (str, optional): The format to save the image in. Defaults to "PNG".
        quality (int, optional): The quality of the saved image (for formats that support it). Defaults to 95.

    Raises:
        Exception: If there's an error saving the image.
    """
    try:
        image.save(path, format=format, quality=quality)
        logger.info(f"Image saved at {path}")
    except Exception as e:
        logger.error(f"Failed to save image at {path}: {str(e)}")
        raise e

def load_image(path: Union[str, os.PathLike]) -> Image.Image:
    """
    Loads an image from the specified path.

    Args:
        path (Union[str, os.PathLike]): The path of the image to be loaded.

    Returns:
        Image.Image: The loaded PIL Image object.

    Raises:
        Exception: If there's an error loading the image.
    """
    try:
        with Image.open(path) as img:
            return img.convert('RGB')
    except Exception as e:
        logger.error(f"Failed to load image from {path}: {str(e)}")
        raise e