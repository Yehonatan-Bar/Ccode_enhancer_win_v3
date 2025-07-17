import os
import logging
import zipfile
import sys
from typing import List
from datetime import datetime

# Add parent directory to system path to allow imports from sibling directories
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from logs.setup_logging import setup_logging

# Load config
import json
config_path = os.path.join(project_root, 'config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

# Modify the log file name to match the current file
config['logging']['log_file'] = os.path.basename(__file__).replace('.py', '.log')

# Setup logging for this module
logger = setup_logging(config, __file__)

def compress_images(image_paths: List[str], output_path: str) -> bool:
    """
    Compresses multiple image files into a zip archive.

    Args:
        image_paths (List[str]): List of paths to image files to be compressed
        output_path (str): Path where the zip archive should be created

    Returns:
        bool: True if compression was successful, False otherwise

    Raises:
        FileNotFoundError: If any of the specified image paths don't exist
        PermissionError: If there's no permission to read images or write the zip file
    """
    logger.info("=== Starting image compression operation ===")
    logger.info(f"Number of images to compress: {len(image_paths)}")
    logger.info(f"Output zip file: {output_path}")
    logger.debug(f"Process ID: {os.getpid()}")
    logger.debug(f"Current working directory: {os.getcwd()}")

    try:
        # Verify all image files exist
        logger.debug("Performing preliminary file checks...")
        for image_path in image_paths:
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                raise FileNotFoundError(f"Image file not found: {image_path}")

        # Create zip file
        logger.debug("Creating zip archive...")
        with zipfile.ZipFile(output_path, 'w') as zip_file:
            for image_path in image_paths:
                # Get image file statistics
                image_stats = os.stat(image_path)
                logger.info(f"=== Image File Statistics: {os.path.basename(image_path)} ===")
                logger.info(f"File size: {image_stats.st_size:,} bytes")
                logger.info(f"Last modified: {datetime.fromtimestamp(image_stats.st_mtime)}")
                logger.debug(f"File permissions (octal): {oct(image_stats.st_mode)}")

                # Add image to zip file
                logger.debug(f"Adding {image_path} to zip archive...")
                zip_file.write(image_path, os.path.basename(image_path))

        # Verify zip file creation
        if os.path.exists(output_path):
            zip_stats = os.stat(output_path)
            logger.info("=== Zip Archive Statistics ===")
            logger.info(f"File size: {zip_stats.st_size:,} bytes")
            logger.info(f"Last modified: {datetime.fromtimestamp(zip_stats.st_mtime)}")
            logger.info("=== Image compression operation completed successfully ===")
            return True
        else:
            logger.error("Zip file was not created successfully")
            return False

    except PermissionError as pe:
        logger.error("=== Permission Error ===")
        logger.error(f"Access denied: {str(pe)}")
        logger.debug(f"Current user: {os.getlogin()}")
        return False

    except Exception as e:
        logger.error("=== Unexpected Error ===")
        logger.error(f"Failed to compress images into {output_path}")
        logger.debug(f"Error type: {type(e).__name__}")
        logger.debug(f"Error message: {str(e)}")
        logger.debug(f"Error traceback: {traceback.format_exc()}")
        logger.debug(f"System info: {platform.platform()}")
        logger.debug(f"Python version: {sys.version}")
        return False

if __name__ == "__main__":
    # Example compression operation
    image_paths = [
        r"C:\Users\yonzb\OneDrive\Pictures\image1.jpg",
        r"C:\Users\yonzb\OneDrive\Pictures\image2.png",
        r"C:\Users\yonzb\OneDrive\Pictures\image3.gif"
    ]
    output_zip = r"C:\Users\yonzb\OneDrive\Documents\compressed_images.zip"

    success = compress_images(image_paths, output_zip)

    if success:
        print(f"Images successfully compressed into '{output_zip}'")
    else:
        print("Image compression operation failed")