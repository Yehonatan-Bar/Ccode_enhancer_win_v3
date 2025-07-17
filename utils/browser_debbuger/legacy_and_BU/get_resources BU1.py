from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
from urllib.parse import urlparse
import time

def get_page_resources(url: str) -> list:
    """
    Opens a URL in Chrome and returns a list of all resource requests.
    Leaves the browser open after execution.
    """
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--remote-debugging-port=9222')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    # Initialize driver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Load the URL
        driver.get(url)
        time.sleep(3)  # Wait for resources to load
        
        # Get performance logs
        logs = driver.get_log('performance')
        
        # Process logs to extract resource URLs
        resources = set()  # Using set to avoid duplicates
        for entry in logs:
            try:
                log = json.loads(entry['message'])['message']
                if 'Network.requestWillBeSent' in log['method']:
                    url = log['params']['request']['url']
                    # Skip data: URLs
                    if not url.startswith('data:'):
                        parsed_url = urlparse(url)
                        # Get the path part of the URL
                        path = parsed_url.path
                        if path:
                            # Get the last part of the path (filename)
                            resource_name = path.split('/')[-1]
                            if resource_name:  # Only add if there's actually a filename
                                resources.add(resource_name)
            except Exception as e:
                print(f"Error processing log entry: {e}")
        
        return sorted(list(resources))  # Convert set to sorted list
        
    except Exception as e:
        print(f"Error: {e}")
        return []

def main():
    url = input("Enter URL to analyze: ")
    print("\nAnalyzing resources, please wait...")
    resources = get_page_resources(url)
    
    print("\nFound resources:")
    for i, resource in enumerate(resources, 1):
        print(f"{i}. {resource}")
    
    print(f"\nTotal resources found: {len(resources)}")

if __name__ == "__main__":
    main()
