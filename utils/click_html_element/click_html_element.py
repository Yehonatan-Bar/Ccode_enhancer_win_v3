import logging
import os
import sys
import json
from typing import Tuple, Optional
from selenium import webdriver

if __name__ == '__main__':
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(project_root)
    from utils.click_html_element.browser_opener import browser_opener
    from logs.setup_logging import archive_existing_logs, setup_logging
    from utils.click_html_element.screenshot_taker import take_screenshot
    from utils.click_html_element.element_identifier import construct_element_identifier_prompt
    from utils.click_html_element.element_clicker import element_clicker

else:
    try:
        from utils.click_html_element.browser_opener import browser_opener
        from logs.setup_logging import archive_existing_logs, setup_logging
        from utils.click_html_element.screenshot_taker import take_screenshot
        from utils.click_html_element.element_identifier import construct_element_identifier_prompt
        from utils.click_html_element.element_clicker import element_clicker
    except ImportError:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.append(project_root)
        from utils.click_html_element.browser_opener import browser_opener
        from logs.setup_logging import archive_existing_logs, setup_logging
        from utils.click_html_element.screenshot_taker import take_screenshot
        from utils.click_html_element.element_identifier import construct_element_identifier_prompt
        from utils.click_html_element.element_clicker import element_clicker

# Load the config
with open('config.json', 'r') as f:
    config = json.load(f)

# Modify the log file name
config['logging']['log_file'] = os.path.basename(__file__).replace('.py', '.log')

# Setup logging
logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
os.makedirs(logs_dir, exist_ok=True)
logger = setup_logging(config, __file__)

def click_element(url: str, is_first_click: bool, prompt: str) -> Tuple[Optional[str], Optional[dict], Optional[webdriver.Chrome]]:
    """
    Clicks an HTML element on the specified URL.

    Args:
        url (str): The URL to open.
        is_first_click (bool): Indicates whether this is the first click.
        prompt (str): The prompt to identify which element to click.

    Returns:
        Tuple[Optional[str], Optional[dict], Optional[webdriver.Chrome]]:
            - HTML content as a string (if successful, else None).
            - Display info as a dict (if determined, else None).
            - WebDriver instance if keep_browser_open is True, otherwise None.
    """
    logger.info(f"=== Starting click element operation for URL: {url} ===")
    logger.debug(f"Is first click: {is_first_click}")
    logger.debug(f"Prompt: {prompt}")

    try:
        html_content, display_info, driver, all_links = browser_opener(url, keep_browser_open=True)

        if html_content:
            logger.info("Successfully opened browser and retrieved HTML.")
            logger.debug(f"Found {len(all_links) if all_links else 0} links on the page")
        else:
            logger.error("Failed to open browser or retrieve HTML.")
            return None, None, None

        # Take screenshot before clicking
        if driver:
            screenshot_path = take_screenshot(display_info, driver, is_before=True)
            logger.info(f"Initial screenshot taken: {screenshot_path}")

            # Pass all values to element identifier
            selector = construct_element_identifier_prompt(html_content, prompt, screenshot_path, display_info, all_links)
            logger.info(f"Element identifier returned selector: {selector}")
            print(f"Identified selector: {selector}")

            # Click the element using element_clicker
            if selector:
                updated_html, outcome_message, driver = element_clicker(driver, selector)
                if updated_html:
                    logger.info(f"Element clicked successfully: {outcome_message}")
                    # Take screenshot after clicking
                    after_screenshot_path = take_screenshot(display_info, driver, is_before=False)
                    logger.info(f"Post-click screenshot taken: {after_screenshot_path}")
                    return updated_html, display_info, driver, after_screenshot_path
                else:
                    logger.error(f"Element click failed: {outcome_message}")
                    return None, None, driver
            else:
                logger.warning("No selector identified. Skipping click.")
                return None, None, driver

        return html_content, display_info, driver

    except Exception as e:
        logger.error("=== Unexpected Error ===")
        logger.error(f"An error occurred: {e}")
        return None, None, None
    finally:
        logger.info("=== Click element operation completed ===")

if __name__ == "__main__":
    # Example usage
    #test_url = "https://www.example.com/"
    #test_prompt = "אני מעוניין בעוד מידע"  # Example prompt

    test_url = "https://docs.nebius.com/studio/inference/quickstart"
    test_prompt = "Find informarion about the models"  # Example prompt
    html, display, driver, after_screenshot_path = click_element(test_url, True, test_prompt)

    if html is not None:
        print("\nOperation successful!")
        print(f"HTML length: {len(html)} characters")
        print(f"Display info: {display}")
        if driver:
            print("Browser is kept open for further inspection.")
            # Keep the script running to prevent the browser from closing
            input("Press Enter to close the browser...")
            driver.quit()
    else:
        print("\nOperation failed!")
