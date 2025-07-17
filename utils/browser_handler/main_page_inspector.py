from typing import Optional, Dict, Any, List
import time
from datetime import datetime
import os
from win32gui import GetWindowRect, EnumWindows, IsWindowVisible
import sys
from urllib.parse import urlparse
import json
import traceback
from logs.setup_logging import setup_logging
from utils.browser_handler.browser_manager import BrowserManager

# Load config
import json
with open('config.json', 'r') as f:
    config = json.load(f)

class URLProcessor:
    def __init__(self, screenshot_dir: str = "screenshots"):
        self.screenshot_dir = screenshot_dir
        self.browser_manager = BrowserManager()
        self.logger = setup_logging(config, 'main_page_inspector')
        self.logger.info(f"Initializing URLProcessor with screenshot directory: {screenshot_dir}")
        
        # Create screenshot directory if it doesn't exist
        os.makedirs(screenshot_dir, exist_ok=True)
        self.logger.debug(f"Screenshot directory created/verified: {screenshot_dir}")

    def analyze_url(self, url: str, wait_time: int = 5) -> Optional[Dict[str, Any]]:
        """
        Analyze the given URL and return results.
        """
        try:
            # Start Chrome in debugging mode
            if not self.browser_manager.start_chrome_debugging():
                self.logger.error("Failed to start Chrome debugging")
                return None
                
            # Setup Selenium WebDriver
            if not self.browser_manager.setup_selenium_driver():
                self.logger.error("Failed to setup Selenium WebDriver")
                return None
                
            driver = self.browser_manager.driver
            
            # Load the URL
            driver.get(url)
            time.sleep(wait_time)  # Wait for page to load
            
            # Get window handle and focus
            window_handle = self.browser_manager.find_browser_window(url)
            if window_handle:
                self.browser_manager.focus_window(window_handle)
                window_rect = GetWindowRect(window_handle)
            else:
                window_rect = None
            
            # Take screenshot
            os.makedirs(self.screenshot_dir, exist_ok=True)
            screenshot_path = os.path.join(self.screenshot_dir, f"screenshot_{int(time.time())}.png")
            driver.save_screenshot(screenshot_path)
            
            # Collect page information
            result = {
                'url': url,
                'status_code': 200,  # You might want to get this from requests
                'window_title': driver.title,
                'window_rect': window_rect,
                'screenshot_path': screenshot_path,
                'js_files': self.get_js_files(driver),
                'network_logs': self.process_network_logs(driver)
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing URL: {str(e)}")
            return None
        finally:
            if self.browser_manager.driver:
                self.browser_manager.driver.quit()

    def process_network_logs(self, driver):
        """Process network logs from the browser."""
        logs = driver.get_log('performance')
        network_logs = []
        
        for entry in logs:
            try:
                log = json.loads(entry['message'])['message']
                if 'Network.response' in log['method'] or 'Network.request' in log['method']:
                    network_logs.append(log)
            except Exception as e:
                self.logger.error(f"Error processing network log: {str(e)}")
                
        return network_logs

    def get_js_files(self, driver) -> List[str]:
        """Get list of JavaScript files loaded on the page."""
        js_files = []
        try:
            scripts = driver.find_elements('tag name', 'script')
            for script in scripts:
                src = script.get_attribute('src')
                if src:
                    js_files.append(src)
        except Exception as e:
            self.logger.error(f"Error getting JS files: {str(e)}")
        return js_files

def main_page_inspector(url: str, wait_time: int = 5) -> Optional[Dict[str, Any]]:
    """
    Function to analyze the given URL using the URLProcessor.
    """
    processor = URLProcessor()
    results = processor.analyze_url(url, wait_time)  

    if results:
        # Add output file path to results
        output_file = f"analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results['output_file'] = output_file

        print("\n=== URL Analysis Results ===")
        print(f"✓ URL: {results['url']}")
        print(f"✓ Screenshot saved: {results['screenshot_path']}")
        print(f"✓ Status code: {results['status_code']}")
        print(f"✓ Network requests captured: {len(results['network_logs'])}")
        print(f"✓ JavaScript files found: {len(results['js_files'])}")
        
        # Save detailed results to JSON
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nDetailed results saved to: {output_file}")
    else:
        print("Analysis failed. Check logs for details.")
    return results

def main():
    logger = setup_logging(config, 'main_page_inspector')
    logger.info("Starting main execution")
    
    if len(sys.argv) != 2:
        logger.error("Invalid number of arguments provided")
        print("Usage: python script.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    logger.info(f"Processing URL: {url}")
    
    try:
        result = main_page_inspector(url)

        if result:
            logger.info("Analysis completed successfully")
            print("\n=== URL Analysis Results ===")
            print(f"✓ URL: {result['url']}")
            print(f"✓ Screenshot saved: {result['screenshot_path']}")
            print(f"✓ Status code: {result['status_code']}")
            print(f"✓ Network requests captured: {len(result['network_logs'])}")
            print(f"✓ JavaScript files found: {len(result['js_files'])}")
            
            # Save detailed results to JSON
            output_file = f"analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            logger.info(f"Results saved to file: {output_file}")
            print(f"\nDetailed results saved to: {output_file}")
        else:
            logger.error("Analysis failed - no results returned")
            print("Analysis failed. Check logs for details.")
    except Exception as e:
        logger.critical(f"Critical error in main execution: {str(e)}")
        logger.critical(f"Traceback: {traceback.format_exc()}")
        print("Critical error occurred. Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()