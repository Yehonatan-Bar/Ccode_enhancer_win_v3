import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
from urllib.parse import urlparse
import time
from logs.setup_logging import setup_logging

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

logger = setup_logging(config, 'get_resources')

def get_page_resources(url: str) -> list:
    """
    Opens a URL in Chrome and returns a list of all resource requests.
    Leaves the browser open after execution.
    """
    logger.info(f"Starting resource analysis for URL: {url}")
    
    # Setup Chrome options
    logger.debug("Setting up Chrome options")
    chrome_options = Options()
    chrome_options.add_argument('--remote-debugging-port=9222')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    # Initialize driver
    logger.debug("Initializing Chrome WebDriver")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Load the URL
        logger.info(f"Loading URL: {url}")
        driver.get(url)
        logger.debug("Waiting for resources to load...")
        time.sleep(3)
        
        # Get performance logs
        logger.debug("Retrieving performance logs")
        logs = driver.get_log('performance')
        logger.info(f"Retrieved {len(logs)} performance log entries")
        
        # Process logs to extract resource URLs
        resources = set()  # Using set to avoid duplicates
        logger.debug("Processing performance logs")
        
        for entry in logs:
            try:
                log = json.loads(entry['message'])['message']
                if 'Network.requestWillBeSent' in log['method']:
                    url = log['params']['request']['url']
                    logger.debug(f"Processing request URL: {url}")
                    
                    # Skip data: URLs
                    if not url.startswith('data:'):
                        parsed_url = urlparse(url)
                        # Get the path part of the URL
                        path = parsed_url.path
                        if path:
                            # Get the last part of the path (filename)
                            resource_name = path.split('/')[-1]
                            if resource_name:  # Only add if there's actually a filename
                                logger.debug(f"Found resource: {resource_name}")
                                resources.add(resource_name)
            except KeyError as e:
                logger.debug(f"Skipping log entry - missing key: {e}")
            except Exception as e:
                logger.error(f"Error processing log entry: {str(e)}")
                logger.debug(f"Problematic log entry: {entry}")
        
        logger.info(f"Found {len(resources)} unique resources")
        return sorted(list(resources))  # Convert set to sorted list
        
    except Exception as e:
        logger.error(f"Error during resource collection: {str(e)}")
        return []

def main():
    logger.info("Starting resource collection script")
    url = input("Enter URL to analyze: ")
    print("\nAnalyzing resources, please wait...")
    
    resources = get_page_resources(url)
    
    print("\nFound resources:")
    for resource in resources:
        print(resource)
    
    logger.info(f"Script completed. Found {len(resources)} resources")
    print(f"\nTotal resources found: {len(resources)}")

if __name__ == "__main__":
    main()
