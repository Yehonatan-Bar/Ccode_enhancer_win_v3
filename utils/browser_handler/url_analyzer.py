from typing import Optional, Dict, Any
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import logging
import traceback
from win32gui import GetWindowText 

def url_analyzer(self, url: str, wait_time: int = 5) -> Optional[Dict[str, Any]]:
    """Main method to analyze URL and gather all data."""
    self.logger.info(f"Starting analysis of URL: {url}")
    
    try:
        # Start Chrome with debugging
        if not self.browser_manager.start_chrome_debugging():
            raise Exception("Failed to start Chrome with debugging")

        # Setup Selenium WebDriver
        if not self.browser_manager.setup_selenium_driver():
            raise Exception("Failed to setup Selenium WebDriver")

        # Load the URL
        self.browser_manager.driver.get(url)
        self.logger.info(f"Waiting {wait_time} seconds for page load")
        time.sleep(wait_time)

        # Find and focus window
        window_handle = self.browser_manager.find_browser_window(url)
        if not window_handle:
            raise Exception("Failed to find browser window")

        self.browser_manager.focus_window(window_handle)

        # Capture screenshot
        screenshot_result = self.capture_screenshot(window_handle)
        if not screenshot_result:
            raise Exception("Failed to capture screenshot")

        # Process network logs
        network_logs = self.network_processor.process_network_logs(self.browser_manager.driver)

        # Fetch page content
        response = requests.get(url)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        js_files = [script['src'] for script in soup.find_all('script') if script.get('src')]

        # Compile results
        result = {
            "url": url,
            "content": response.text,
            "screenshot_path": screenshot_result["screenshot_path"],
            "window_handle": window_handle,
            "window_title": GetWindowText(window_handle),
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "js_files": js_files,
            "network_logs": network_logs,
            "timestamp": datetime.now().isoformat(),
            "window_rect": screenshot_result["window_rect"]
        }

        return result

    except Exception as e:
        self.logger.error(f"Error analyzing URL: {str(e)}")
        self.logger.debug(f"Traceback: {traceback.format_exc()}")
        return None

    finally:
        if self.browser_manager.driver:
            self.browser_manager.driver.quit()

def capture_screenshot(self, window_handle) -> Optional[Dict[str, Any]]:
    """
    Captures a screenshot of the specified window handle.
    
    Args:
        window_handle: The handle of the window to capture
        
    Returns:
        Dictionary containing screenshot path and window dimensions, or None if failed
    """
    try:
        from PIL import ImageGrab
        import win32gui
        import os
        from datetime import datetime
        
        # Get the window rectangle
        left, top, right, bottom = win32gui.GetWindowRect(window_handle)
        window_rect = {
            "left": left,
            "top": top,
            "right": right,
            "bottom": bottom
        }
        
        # Capture the specified region
        screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
        
        # Create screenshots directory if it doesn't exist
        screenshots_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        
        # Generate unique filename using timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(screenshots_dir, f"screenshot_{timestamp}.png")
        
        # Save the screenshot
        screenshot.save(screenshot_path)
        
        return {
            "screenshot_path": screenshot_path,
            "window_rect": window_rect
        }
        
    except Exception as e:
        self.logger.error(f"Error capturing screenshot: {str(e)}")
        return None
