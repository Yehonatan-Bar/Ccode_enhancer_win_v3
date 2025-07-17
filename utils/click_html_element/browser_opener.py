import logging
import os
import sys
import json
import platform
import traceback
from typing import Tuple, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import screeninfo
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import time

if __name__ == '__main__':
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(project_root)
    from logs.setup_logging import archive_existing_logs, setup_logging
else:
    try:
        from logs.setup_logging import archive_existing_logs, setup_logging
    except ImportError:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.append(project_root)
        from logs.setup_logging import archive_existing_logs, setup_logging

# Load the config
with open('config.json', 'r') as f:
    config = json.load(f)

# Modify the log file name
config['logging']['log_file'] = os.path.basename(__file__).replace('.py', '.log')

# Setup logging
logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
os.makedirs(logs_dir, exist_ok=True)
logger = setup_logging(config, __file__)

def browser_opener(url: str, target_element_selector: dict = None, keep_browser_open: bool = True, wait_timeout: int = 20, check_visibility: bool = False) -> Tuple[Optional[str], Optional[dict], Optional[webdriver.Chrome], Optional[list]]:
    """
    Opens Chrome browser at the specified URL and returns HTML content, display info,
    WebDriver instance (optional), and list of all links found.

    Args:
        url (str): The URL to open.
        target_element_selector (dict): Dictionary containing CSS and/or XPath selectors
                                      for the target element to wait for.
                                      Format: {'css': 'selector', 'xpath': 'selector'}
        keep_browser_open (bool): If True, the browser will remain open. Defaults to True.
        wait_timeout (int): Maximum time to wait for elements in seconds. Defaults to 20.
        check_visibility (bool): If True, waits for element visibility instead of just presence.
                               Defaults to False.

    Returns:
        Tuple[Optional[str], Optional[dict], Optional[webdriver.Chrome], Optional[list]]:
            - HTML content as string (if successful, else None)
            - Display info as dict (if determined, else None)
            - WebDriver instance if keep_browser_open is True, else None
            - List of all links found (if successful, else None)
    """
    logger.info(f"=== Starting browser operation for URL: {url} ===")
    logger.debug(f"Process ID: {os.getpid()}")
    logger.debug(f"System platform: {platform.platform()}")

    driver = None
    display_info = None  # Initialize as None for consistency

    try:
        logger.debug("Setting up Chrome options...")
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--enable-javascript')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL', 'browser': 'ALL'})
        # Additional Chrome options:
        chrome_options.add_argument("--disable-gpu")  # לעיתים עוזר בפתרון בעיות רנדור
        chrome_options.add_argument("--no-sandbox")  # נסה להוסיף רק אם אתה בטוח בסביבה שלך (בדרך כלל Docker או סביבות מבודדות)
        chrome_options.add_argument("--disable-dev-shm-usage")  # לעיתים עוזר ב-Linux/Docker
        logger.debug(f"Chrome options set: {chrome_options.arguments}")

        logger.info("Initializing Chrome WebDriver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.debug(f"WebDriver session ID: {driver.session_id}")

        logger.info(f"Navigating to URL: {url}")
        driver.get(url)
        logger.debug(f"First 500 chars of HTML after driver.get: {driver.page_source[:500]}")

        # Log document ready state before waiting
        logger.debug(f"Document readyState before wait: {driver.execute_script('return document.readyState')}")
        logger.info("Waiting for document ready state...")
        WebDriverWait(driver, wait_timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        # Log document ready state after waiting
        logger.debug(f"Document readyState after wait: {driver.execute_script('return document.readyState')}")
        logger.debug("Document ready state achieved.")

        # Wait for target element if specified
        if target_element_selector:
            target_element = None
            css_selector = target_element_selector.get('css')
            xpath_selector = target_element_selector.get('xpath')

            # Choose wait condition based on check_visibility parameter
            wait_condition = EC.visibility_of_element_located if check_visibility else EC.presence_of_element_located

            if css_selector:
                logger.info(f"Waiting for target element using CSS Selector: '{css_selector}'")
                try:
                    target_element = WebDriverWait(driver, wait_timeout).until(
                        wait_condition((By.CSS_SELECTOR, css_selector))
                    )
                    logger.info("Target element found using CSS Selector!")
                except TimeoutException:
                    logger.warning(f"Timeout waiting for CSS Selector: '{css_selector}'. Trying XPath...")

            if not target_element and xpath_selector:
                logger.info(f"Waiting for target element using XPath: '{xpath_selector}'")
                try:
                    target_element = WebDriverWait(driver, wait_timeout).until(
                        wait_condition((By.XPATH, xpath_selector))
                    )
                    logger.info("Target element found using XPath!")
                except TimeoutException:
                    logger.error(f"Timeout waiting for XPath: '{xpath_selector}'. Target element not found.")
                    return None, None, None, None

            if not target_element:
                logger.error("No target element found using either CSS or XPath.")
                return None, None, None, None

            # Scroll target element into view
            driver.execute_script("arguments[0].scrollIntoView(true);", target_element)
            time.sleep(0.5)
            logger.debug("Scrolled target element into view.")

        # Collect all links with more specific exception handling
        all_links_data = []
        all_links = driver.find_elements(By.TAG_NAME, 'a')
        logger.info(f"Found {len(all_links)} links on the page.")
        
        for link in all_links:
            try:
                href = link.get_attribute('href')
                text = link.text
                all_links_data.append({'text': text, 'href': href})
            except NoSuchElementException:
                logger.warning("Skipped a link due to NoSuchElementException")
                continue
            except StaleElementReferenceException:
                logger.warning("Skipped a link due to StaleElementReferenceException")
                continue
            except Exception as e:
                logger.error(f"Unexpected error while processing link: {str(e)}")
                continue

        logger.debug(f"Current page title: {driver.title}")
        
        logger.debug("Retrieving page HTML...")
        # Get HTML after all dynamic content has loaded
        html_content = driver.page_source
        html_length = len(html_content)
        logger.info(f"HTML content retrieved: {html_length:,} characters")
        logger.debug(f"First 200 characters: {html_content[:200]}")
        logger.debug(f"Full HTML content: {html_content}")

        logger.info("Retrieving display information...")
        displays = screeninfo.get_monitors()
        logger.debug(f"Number of displays detected: {len(displays)}")

        current_window = driver.get_window_position()
        window_size = driver.get_window_size()
        logger.debug(f"Window position: {current_window}")
        logger.debug(f"Window size: {window_size}")

        for display in displays:
            logger.debug(f"Checking display: {display}")
            if (current_window['x'] >= display.x and
                current_window['x'] < display.x + display.width):
                display_info = {
                    'display_number': displays.index(display) + 1,
                    'width': display.width,
                    'height': display.height,
                    'x': display.x,
                    'y': display.y,
                    'is_primary': display.is_primary
                }
                logger.info(f"Browser detected on display: {display_info['display_number']}")
                break

        if not display_info:
            logger.warning("No matching display found for the browser window position.")
            # Fallback to primary monitor if available
            for disp in displays:
                if disp.is_primary:
                    display_info = {
                        'display_number': displays.index(disp) + 1,
                        'width': disp.width,
                        'height': disp.height,
                        'x': disp.x,
                        'y': disp.y,
                        'is_primary': disp.is_primary
                    }
                    logger.info(f"Falling back to primary display: {display_info['display_number']}")
                    break

        if not display_info:
            logger.error("No display information could be determined.")
            display_info = None

        logger.info("=== Browser operation completed successfully ===")

        # Save HTML content to a temporary file for debugging purposes
        logger.debug("Saving HTML content to debug_html.html")
        with open("debug_html.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        logger.debug("HTML content saved.")

        result_driver = driver if keep_browser_open else None
        return html_content, display_info, result_driver, all_links_data

    except Exception as e:
        logger.error("=== Unexpected Error ===")
        logger.error("Failed to complete browser operation")
        logger.debug(f"Error type: {type(e).__name__}")
        logger.debug(f"Error message: {str(e)}")
        logger.debug(f"Error traceback: {traceback.format_exc()}")
        if driver:
            driver.quit()
        return None, None, None, None

    finally:
        if driver and not keep_browser_open:
            logger.debug("Closing WebDriver as keep_browser_open is set to False.")
            driver.quit()
            logger.debug("WebDriver closed successfully")
        elif driver:
            logger.debug("Keeping WebDriver open as keep_browser_open is True.")

if __name__ == "__main__":
    # Example usage with target element selector
    test_url = "https://br7news.co.il/he/business-articles"
    target_selector = {
        'css': '#wrapper > header > section.sec-header-bottom > div > nav > ul > li:nth-child(5) > a',
        'xpath': '//*[@id="wrapper"]/header/section[2]/div/nav/ul/li[5]/a'
    }
    
    html, display, driver, all_links = browser_opener(
        test_url, 
        target_element_selector=target_selector,
        keep_browser_open=True
    )

    if html is not None:
        print("\nOperation successful!")
        print(f"HTML length: {len(html)} characters")
        print(f"Display info: {display}")

        print("\n--- All Links on the page ---")
        for link_data in all_links:
            print(f"Link Text: {link_data['text']}, Href: {link_data['href']}")

        if driver:
            print("\nBrowser is kept open for further inspection.")
            input("Press Enter to close the browser...")
            driver.quit()
    else:
        print("\nOperation failed!")
