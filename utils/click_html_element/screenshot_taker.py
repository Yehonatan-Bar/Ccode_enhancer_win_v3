import os
import shutil
import logging
from datetime import datetime
from selenium import webdriver
import pyautogui
import time

# Assuming logs are set up in browser_opener, just configure this module's logger
logger = logging.getLogger(__name__)

def take_screenshot(display_info: dict, driver: webdriver.Chrome, is_before: bool) -> str:
    """
    Takes a screenshot using the provided WebDriver and saves it to the appropriate directory.
    Archives existing screenshots if necessary.

    Args:
        display_info (dict): Information about the display, used for naming the screenshot.
        driver (webdriver.Chrome): The WebDriver instance.
        is_before (bool): True if the screenshot is taken before a click, False otherwise.

    Returns:
        str: The path to the saved screenshot.
    """
    # Add 5 second wait for page to load
    logger.info("Waiting 5 seconds for page to load...")
    time.sleep(5)
    
    screenshots_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'screenshots')
    before_click_dir = os.path.join(screenshots_dir, 'before_click')
    after_click_dir = os.path.join(screenshots_dir, 'after_click')
    archives_dir = os.path.join(screenshots_dir, 'archives')

    os.makedirs(before_click_dir, exist_ok=True)
    os.makedirs(after_click_dir, exist_ok=True)
    os.makedirs(archives_dir, exist_ok=True)

    if is_before:
        # Archive existing screenshots in before_click
        logger.info("Archiving existing screenshots...")
        for filename in os.listdir(before_click_dir):
            if filename.endswith('.png'):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_filename = f"{filename.replace('.png', '')}_{timestamp}.png"
                shutil.move(os.path.join(before_click_dir, filename), os.path.join(archives_dir, new_filename))
                logger.debug(f"Moved '{filename}' to '{archives_dir}'")

        screenshot_dir = before_click_dir
    else:
        screenshot_dir = after_click_dir
        logger.info("Archiving existing screenshots...")
        for filename in os.listdir(after_click_dir):
            if filename.endswith('.png'):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_filename = f"{filename.replace('.png', '')}_{timestamp}.png"
                shutil.move(os.path.join(after_click_dir, filename), os.path.join(archives_dir, new_filename))
                logger.debug(f"Moved '{filename}' to '{archives_dir}'")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    display_num = display_info['display_number'] if display_info and 'display_number' in display_info else 'unknown'
    screenshot_name = f"screenshot_{timestamp}_display_{display_num}.png"
    screenshot_path = os.path.join(screenshot_dir, screenshot_name)

    logger.info(f"Taking screenshot and saving to: {screenshot_path}")
    # Use pyautogui to take a screenshot of the entire screen
    screen_width, screen_height = pyautogui.size()
    #calculate top left corner of display
    display_x_start = display_info['x']
    display_y_start = display_info['y']

    region = (display_x_start, display_y_start, display_x_start + display_info['width'],
              display_y_start + display_info['height'])
    screenshot = pyautogui.screenshot(region=region)
    screenshot.save(screenshot_path)
    logger.info(f"Screenshot saved successfully.")
    return screenshot_path

if __name__ == "__main__":
    # Example Usage
    # You'll need a running WebDriver instance for this to work.  This example
    # assumes you've used browser_opener.py to start a browser and have the
    # driver and display_info.  It also assumes you have a config.json file.
    from browser_opener import browser_opener

    # Use browser_opener to start the browser.
    test_url = "https://www.example.com"
    html_content, display_info, driver = browser_opener(test_url, keep_browser_open=True)

    if driver:
        try:
            # Take a screenshot *before* a hypothetical click.
            screenshot_path_before = take_screenshot(display_info, driver, is_before=True)
            print(f"Screenshot (before click) saved to: {screenshot_path_before}")

            # Simulate a click or other action here...

            # Take a screenshot *after* the hypothetical click.
            screenshot_path_after = take_screenshot(display_info, driver, is_before=False)
            print(f"Screenshot (after click) saved to: {screenshot_path_after}")

        finally:
            # Make sure to close the driver.
            driver.quit()
            print("Browser closed.")
    else:
        print("Failed to open browser, so no screenshot was taken.")