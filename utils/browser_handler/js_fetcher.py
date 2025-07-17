import win32gui
import json
import logging
from typing import Dict, Optional, List
from urllib.parse import urljoin
import requests
from logs.setup_logging import setup_logging

# Load config and setup logging
with open('config.json', 'r') as f:
    config = json.load(f)

logger = setup_logging(config, __file__)

class JSFetcher:
    def __init__(self, window_handle: int, base_url: str):
        self.window_handle = window_handle
        self.base_url = base_url
        self.window_title = win32gui.GetWindowText(window_handle)
    
    def fetch_js_files(self, js_urls: List[str]) -> Dict[str, Optional[str]]:
        """Fetch JavaScript files from the active browser window.
        
        Args:
            js_urls: List of JavaScript URLs (can be relative or absolute)
            
        Returns:
            Dictionary mapping JS URLs to their contents
        """
        js_contents = {}
        
        for js_url in js_urls:
            try:
                # Handle relative URLs
                full_url = urljoin(self.base_url, js_url)
                response = requests.get(full_url)
                response.raise_for_status()
                js_contents[js_url] = response.text
                logger.info(f"Successfully fetched JS file: {js_url}")
            except Exception as e:
                logger.error(f"Failed to fetch JS file {js_url}: {str(e)}")
                js_contents[js_url] = None
                
        return js_contents

def js_fetcher(window_handle: int, base_url: str, js_urls: List[str]) -> Dict[str, Optional[str]]:
    """
    Utility function to fetch JavaScript files using the JSFetcher class.
    
    Args:
        window_handle (int): Handle to the browser window
        base_url (str): Base URL for resolving relative JavaScript URLs
        js_urls (List[str]): List of JavaScript URLs to fetch (absolute or relative)
    
    Returns:
        Dict[str, Optional[str]]: Dictionary mapping JavaScript URLs to their contents
                                 None values indicate failed fetches
    
    Example:
        js_files = fetch_javascript_files(
            window_handle=12345,
            base_url="https://example.com",
            js_urls=["main.js", "/static/vendor.js"]
        )
    """
    fetcher = JSFetcher(window_handle, base_url)
    return fetcher.fetch_js_files(js_urls)