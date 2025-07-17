import sys
import os
import logging
from datetime import datetime

# Import the updated open_url and take_screenshot modules
from utils.click_on_elemnt.open_browser_and_get_handle import open_browser_and_get_handle
from utils.click_on_elemnt.bring_to_front_and_screenshot import bring_to_front_and_screenshot

# If you have custom logging utilities (like in get_element_desc.py), import them here.
# For example:
# from utils.logging_utils import setup_logging_directory, setup_logger

# Below are stubs for setup_logging_directory and setup_logger. Replace them with your actual implementations.
def setup_logging_directory():
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    return logs_dir

def setup_logger(name, log_file, level=logging.INFO, fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', console_out=True):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # File handler
    file_handler = logging.FileHandler(log_file, mode='a')
    file_formatter = logging.Formatter(fmt)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler
    if console_out:
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(fmt)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger

def navigate_and_screenshot(url):
    """
    1. Opens the given URL in the default browser using open_url.py (with logging).
    2. Retrieves the browser window handle.
    3. Brings that window to the front using take_screenshot.py (with logging).
    4. Takes a screenshot of the screen.
    5. Prints the screenshot file path.
    """

    # Setup logging
    logs_dir = setup_logging_directory()
    log_file = os.path.join(
        logs_dir,
        f"navigate_and_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    logger = setup_logger(
        'navigate_and_screenshot',
        log_file,
        logging.INFO,
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        True
    )

    logger.info("=== Starting navigate_and_screenshot script ===")
    logger.info(f"URL received: {url}")

    hwnd = None
    try:
        logger.info("Attempting to open the browser and retrieve a window handle...")
        hwnd = open_browser_and_get_handle(url, logger)
        if hwnd:
            logger.info(f"Found window handle (HWND): {hwnd}")
            print(f"Found window handle (HWND): {hwnd}")

            logger.info("Bringing the browser to the front and taking a screenshot...")
            screenshot_path = bring_to_front_and_screenshot(hwnd, logger)
            logger.info(f"Screenshot saved to: {screenshot_path}")
            print(f"Screenshot saved to: {screenshot_path}")
        else:
            logger.warning("Could not find the browser window for the given URL.")
            print("Could not find the browser window for the given URL.")
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python navigate_and_screenshot.py <URL>")
        sys.exit(1)

    url_to_open = sys.argv[1]
    navigate_and_screenshot(url_to_open)