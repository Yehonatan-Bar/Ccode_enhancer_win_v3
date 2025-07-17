import subprocess
import time
import logging
import sys
from datetime import datetime
import os


# Point to the actual root directory of your project
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logging_utils import setup_logging_directory, setup_logger

def click_element(element_id, url=None, timeout=10):
    """
    Automatically opens Chrome with debugging, connects to it, and clicks the specified element.
    
    :param element_id: The ID of the element to click
    :param url: Optional URL to navigate to. If None, will use current page
    :param timeout: Maximum time to wait for element
    """

    # Move the logging logic inside this function
    logs_dir = setup_logging_directory()
    log_file = os.path.join(
        logs_dir,
        f"click_element_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    logger = setup_logger(
        'click_element',
        log_file,
        logging.INFO,
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        True
    )

    logger.info("=== Starting auto_click operation ===")
    logger.info(f"Target element ID: {element_id}")
    logger.info(f"URL: {url if url else 'Using current page'}")
    logger.info(f"Timeout setting: {timeout} seconds")

    try:
        # Kill existing Chrome processes
        logger.info("Attempting to close existing Chrome instances")
        os.system("taskkill /f /im chrome.exe")
        time.sleep(1)
        logger.debug("Waited 1 second after closing Chrome")
        
        # Start Chrome with remote debugging
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        logger.info(f"Starting Chrome with debugging from path: {chrome_path}")
        subprocess.Popen([chrome_path, "--remote-debugging-port=9222"])
        time.sleep(5)
        logger.debug("Waited 5 seconds for Chrome to initialize")
        
        # Connect to the browser
        logger.info("Configuring Chrome options")
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        logger.info("Initializing Chrome WebDriver")
        driver = webdriver.Chrome(options=chrome_options)
        
        # Navigate if URL provided
        if url:
            logger.info(f"Navigating to URL: {url}")
            driver.get(url)
        
        # Wait for and click element
        logger.info(f"Waiting for element with ID '{element_id}' to be clickable (timeout: {timeout}s)")
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.ID, element_id))
        )
        logger.info("Element found, attempting to click")
        element.click()
        logger.info("Element clicked successfully")
        
        return True
    except Exception as e:
        logger.error("=== Error during auto_click operation ===")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.debug(f"Traceback: {e.__traceback__}")
        return False

def main():
    """
    Main function that executes the click_element function.
    
    Usage (from cmd):
      python click_element.py <element_id> [url]
    
    Example:
      python click_element.py "login-button" "https://example.com"
    """
    if len(sys.argv) < 2:
        print("Usage: python click_element.py <element_id> [url]")
        sys.exit(1)

    element_id = sys.argv[1]
    url = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        result = click_element(element_id, url=url)
        if result:
            print("Element clicked successfully")
        else:
            print("Failed to click element")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
