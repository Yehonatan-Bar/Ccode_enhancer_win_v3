import logging
import os
import sys
import json
from typing import Tuple, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException
import time

if __name__ == '__main__':
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(project_root)
    from utils.click_html_element.browser_opener import browser_opener
    from logs.setup_logging import setup_logging
    from utils.click_html_element.screenshot_taker import take_screenshot

else:
    try:
        from utils.click_html_element.browser_opener import browser_opener
        from logs.setup_logging import setup_logging
        from utils.click_html_element.screenshot_taker import take_screenshot
    except ImportError:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.append(project_root)
        from utils.click_html_element.browser_opener import browser_opener
        from logs.setup_logging import setup_logging
        from utils.click_html_element.screenshot_taker import take_screenshot

# Load the config
with open('config.json', 'r') as f:
    config = json.load(f)

# Modify the log file name
config['logging']['log_file'] = os.path.basename(__file__).replace('.py', '.log')

# Setup logging
logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
os.makedirs(logs_dir, exist_ok=True)
logger = setup_logging(config, __file__)


def element_clicker(driver: webdriver.Chrome, selector: str) -> Tuple[Optional[str], Optional[dict], Optional[webdriver.Chrome]]:
    """
    Clicks an HTML element using the provided selector.

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        selector (str): The CSS selector or XPath to identify the element.

    Returns:
        Tuple[Optional[str], Optional[str], Optional[webdriver.Chrome]]:
            - Updated HTML content as a string (if successful, else None).
            - Message indicating the outcome of the click operation.
            - WebDriver instance.
    """
    logger.info("=== Starting element clicker operation ===")
    
    # Handle case where selector is passed as a dictionary
    if isinstance(selector, dict):
        selector = selector.get('selector', '')
    
    logger.debug(f"Selector received: {selector}")

    outcome_message = None  # Initialize outcome_message

    try:
        if selector.startswith('xpath:'):
            by_method = By.XPATH
            selector = selector[len('xpath:'):]  # Remove the prefix to get the actual selector
            logger.debug(f"XPath selector detected: {selector}")
        else:
            by_method = By.CSS_SELECTOR
            logger.debug(f"CSS selector detected: {selector}")

        element = driver.find_element(by=by_method, value=selector)
        logger.info(f"Element found with selector: {selector}")

        # Scroll element into view before clicking
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)  # Short pause after scrolling, before click
        logger.debug("Scrolled element into view.")

        element.click()
        logger.info("Element clicked successfully.")
        outcome_message = "Element clicked successfully"


    except NoSuchElementException:
        logger.error(f"Element not found with selector: {selector}")
        outcome_message = "Element not found"
        return None, outcome_message, driver  # Return None for HTML content and the outcome message

    except ElementNotInteractableException:
        logger.error(f"Element not interactable with selector: {selector}")
        outcome_message = "Element not interactable"
        return None, outcome_message, driver

    except ElementClickInterceptedException:
        logger.error(f"Element click intercepted with selector: {selector}")
        outcome_message = "Element click intercepted"
        return None, outcome_message, driver

    except StaleElementReferenceException:
        logger.error(f"Stale element reference with selector: {selector}")
        outcome_message = "Stale element reference"
        return None, outcome_message, driver

    except Exception as e:
        logger.error(f"Error clicking element with selector: {selector}")
        logger.error(f"Error details: {e}")
        outcome_message = f"Error clicking element: {e}"
        return None, outcome_message, driver # Return None for HTML content and the outcome message

    finally:
        updated_html_content = driver.page_source
        logger.info("=== Element clicker operation completed ===")
        return updated_html_content, outcome_message, driver


if __name__ == "__main__":
    # Example usage (for testing purposes only)
    test_url = "https://www.example.com/"
    test_selector = "a[href='https://www.iana.org/domains/example']"  # Example CSS selector

    html_content, display_info, driver, all_links = browser_opener(test_url, keep_browser_open=True)
    if driver:
        updated_html, outcome_message, driver = element_clicker(driver, test_selector)

        if updated_html:
            print("\nElement click operation successful!")
            print(f"Outcome message: {outcome_message}")
            print(f"Updated HTML length: {len(updated_html)} characters")
            # You can save or further process updated_html here
        else:
            print("\nElement click operation failed.")
            print(f"Outcome message: {outcome_message}")

        print("\nBrowser is kept open for further inspection.")
        input("Press Enter to close the browser...")
        driver.quit()
    else:
        print("\nBrowser opening failed, cannot proceed with element click test.")
