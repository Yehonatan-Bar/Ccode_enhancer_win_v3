import sys
import time
import os
import logging
import win32gui
import win32con
import pyautogui
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# If you have a logging utils module like in get_element_desc.py, import it here.
# For example:
# from utils.logging_utils import setup_logging_directory, setup_logger

# Placeholder stubs for setup_logging_directory and setup_logger:
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

def bring_to_front_and_screenshot(url):
    """
    Capture a screenshot using the provided Selenium WebDriver instance.
    """
    
    logs_dir = setup_logging_directory()
    log_file = os.path.join(logs_dir, "take_screenshot.log")
    logger = setup_logger("take_screenshot", log_file, level=logging.INFO)

    logger.info("Preparing to capture screenshot via Selenium...")
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(2)  # Wait for page load
    # Optionally, maximize or focus the current window
    driver.maximize_window()
    time.sleep(1)

    # Create/verify a screenshots folder
    screenshots_dir = r"C:\scripts\screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)

    # Generate a timestamped filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    screenshot_path = os.path.join(screenshots_dir, f"browser_screenshot_{timestamp}.png")

    # Let Selenium handle the screenshot
    driver.save_screenshot(screenshot_path)
    logger.info(f"Screenshot saved to: {screenshot_path}")

    # Cleanup
    driver.quit()
    logger.info("Browser closed and script finished.")
    return screenshot_path

def main():
    """
    Standalone usage:
    python take_screenshot.py

    This example simply shows how to instantiate a driver and call bring_to_front_and_screenshot.
    In production, you may import bring_to_front_and_screenshot(driver, logger) from elsewhere.
    """
    
    logs_dir = setup_logging_directory()
    log_file = os.path.join(logs_dir, "take_screenshot.log")
    logger = setup_logger("take_screenshot", log_file, level=logging.INFO)

    logger.info("=== Starting screenshot tool (Selenium-based) ===")
    
    url = "https://example.com"
    image_path = bring_to_front_and_screenshot(url)
    print(f"Screenshot captured: {image_path}")


if __name__ == "__main__":
    main()