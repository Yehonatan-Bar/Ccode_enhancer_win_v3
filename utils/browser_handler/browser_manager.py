import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import time
import subprocess
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from win32gui import GetWindowText, IsWindowVisible, EnumWindows, ShowWindow, SetForegroundWindow
from win32gui import GetWindowRect
import win32con
from urllib.parse import urlparse
from typing import Optional
from logs.setup_logging import setup_logging

# Load config
import json
with open('config.json', 'r') as f:
    config = json.load(f)

class BrowserManager:
    def __init__(self, debug_port: str = "9222", headless: bool = False):
        self.debug_port = debug_port
        self.headless = headless
        self.chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        self.driver = None
        self.logger = setup_logging(config, 'browser_manager')
        self.chrome_process = None # Added to store subprocess handle
        
    def start_chrome_debugging(self) -> bool:
        """Start Chrome with remote debugging enabled if not already running, with retries and checks."""
        self.logger.info(f"Attempting to ensure Chrome is running with debugging on port {self.debug_port}")
        
        # Define the user data directory for the debugging instance
        user_data_dir_path = os.path.join(os.getcwd(), "chrome_debug_profile") 

        try:
            # Check if Chrome is already running with debugging on the specified port
            requests.get(f'http://localhost:{self.debug_port}/json/version', timeout=1)
            self.logger.info(f"Chrome already running with debugging on port {self.debug_port}")
            return True
        except requests.exceptions.ConnectionError:
            self.logger.info(f"Chrome not found on port {self.debug_port}. Attempting to start a new instance.")
            try:
                # Ensure the user_data_dir_path exists
                os.makedirs(user_data_dir_path, exist_ok=True)
                self.logger.debug(f"User data directory for debugging: {user_data_dir_path}")

                cmd = [
                    self.chrome_path,
                    f'--remote-debugging-port={self.debug_port}',
                    f'--user-data-dir={user_data_dir_path}',
                    '--no-first-run',
                    '--no-default-browser-check',
                    '--disable-extensions',
                    '--disable-popup-blocking',
                    '--disable-background-networking',
                    '--disable-sync',
                    '--disable-translate',
                    '--disable-web-security', # Added back based on previous attempts
                    '--disable-features=VizDisplayCompositor' # Added back based on previous attempts
                ]
                self.logger.info(f"Starting Chrome with command: {' '.join(cmd)}")
                self.chrome_process = subprocess.Popen(cmd)
                
                # Wait for Chrome to start and debugging port to be available
                max_wait_time = 30  # seconds
                start_time = time.time()
                while time.time() - start_time < max_wait_time:
                    try:
                        requests.get(f'http://localhost:{self.debug_port}/json/version', timeout=1)
                        self.logger.info(f"Successfully started and connected to Chrome debugging on port {self.debug_port} after {time.time() - start_time:.2f} seconds.")
                        return True
                    except requests.exceptions.ConnectionError:
                        time.sleep(0.5)
                    except requests.exceptions.Timeout:
                        self.logger.warning(f"Connection to {self.debug_port} timed out during check, retrying...")
                        time.sleep(0.5)
                
                self.logger.error(f"Failed to connect to Chrome debugging on port {self.debug_port} after {max_wait_time} seconds.")
                if self.chrome_process:
                    self.logger.info("Terminating unresponsive Chrome process.")
                    self.chrome_process.terminate()
                    self.chrome_process.wait(timeout=5) # Wait for process to terminate
                return False
            except subprocess.TimeoutExpired:
                self.logger.error("Chrome process did not terminate in time.")
                return False
            except Exception as e:
                self.logger.error(f"Failed to start Chrome for debugging: {str(e)}")
                self.logger.error(traceback.format_exc())
                if self.chrome_process:
                    self.chrome_process.terminate()
                return False
        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout when checking if Chrome is running on port {self.debug_port}. It might be slow or unresponsive.")
            return False
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while checking or starting Chrome: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False

    def setup_selenium_driver(self):
        """Initialize Selenium WebDriver with appropriate options."""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        
        # Connect to existing Chrome instance instead of starting new one
        chrome_options.add_experimental_option("debuggerAddress", f"localhost:{self.debug_port}")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.logger.info("Selenium WebDriver initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {str(e)}")
            return False

    def find_browser_window(self, url: str) -> Optional[int]:
        """Find the specific Chrome window containing the given URL."""
        domain = urlparse(url).netloc
        self.logger.debug(f"Searching for window with domain: {domain}")
        
        def callback(hwnd, windows):
            if IsWindowVisible(hwnd):
                title = GetWindowText(hwnd)
                if domain.lower() in title.lower() and 'chrome' in title.lower():
                    windows.append(hwnd)
        
        windows = []
        EnumWindows(callback, windows)
        return windows[0] if windows else None

    def focus_window(self, window_handle: int) -> bool:
        """Focus on a specific window."""
        try:
            ShowWindow(window_handle, win32con.SW_MAXIMIZE)
            SetForegroundWindow(window_handle)
            return True
        except Exception as e:
            self.logger.error(f"Failed to focus window: {str(e)}")
            return False
