from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from datetime import datetime
import argparse
from typing import Dict, List
import logging
import os

def setup_logging_directory():
    """Create logs directory if it doesn't exist"""
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir

class NetworkAnalyzer:
    def __init__(self, headless: bool = True):
        """Initialize the NetworkAnalyzer with Chrome options."""
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--log-level=3')  # Suppress console logging
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Enable performance logging
        self.chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        self.driver = None
        self.requests = []

    def setup_logging(self):
        """Setup logging configuration."""
        logs_dir = setup_logging_directory()
        log_file = os.path.join(logs_dir, 'network_reader.log')
        
        # Configure logger
        self.logger = logging.getLogger(__name__ + '.network_analyzer')
        self.logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Add handlers
        file_handler = logging.FileHandler(log_file)
        console_handler = logging.StreamHandler()
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Prevent logging from propagating to the root logger
        self.logger.propagate = False

    def start_browser(self):
        """Start the Chrome browser with configured options."""
        try:
            self.driver = webdriver.Chrome(options=self.chrome_options)
        except Exception as e:
            self.logger.error(f"Failed to start browser: {str(e)}")
            raise

    def process_network_logs(self) -> List[Dict]:
        """Process and filter relevant network logs."""
        logs = self.driver.get_log('performance')
        
        for entry in logs:
            try:
                log = json.loads(entry['message'])['message']
                
                if 'Network.requestWillBeSent' in log['method']:
                    request = log['params']['request']
                    self.requests.append({
                        'url': request['url'],
                        'method': request['method'],
                        'type': 'Unknown',  # Will be updated when response is received
                        'timestamp': datetime.fromtimestamp(log['params']['timestamp']).strftime('%Y-%m-%d %H:%M:%S.%f')
                    })
                
                elif 'Network.responseReceived' in log['method']:
                    response = log['params']['response']
                    request_url = response['url']
                    
                    # Update the corresponding request with response info
                    for req in self.requests:
                        if req['url'] == request_url:
                            req['type'] = response.get('mimeType', 'Unknown')
                            req['status'] = response.get('status', 0)
                            break
                            
            except (KeyError, json.JSONDecodeError) as e:
                self.logger.warning(f"Error processing log entry: {str(e)}")
                continue
                
        return self.requests

    def analyze_url(self, url: str) -> List[Dict]:
        """
        Analyze a URL and return all network requests made during page load.
        
        Args:
            url (str): The URL to analyze
            
        Returns:
            List[Dict]: List of network requests with their details
        """
        try:
            self.setup_logging()
            self.start_browser()
            
            self.logger.info(f"Analyzing URL: {url}")
            self.driver.get(url)
            
            # Wait for the page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(('tag name', 'body'))
            )
            
            # Process network logs
            requests = self.process_network_logs()
            
            # Group requests by type
            request_types = {}
            for req in requests:
                req_type = req['type']
                if req_type not in request_types:
                    request_types[req_type] = 0
                request_types[req_type] += 1
            
            self.logger.info("\nRequest summary by type:")
            for req_type, count in request_types.items():
                self.logger.info(f"{req_type}: {count} requests")
                
            return requests
            
        except Exception as e:
            self.logger.error(f"Error analyzing URL: {str(e)}")
            raise
            
        finally:
            if self.driver:
                self.driver.quit()
                
def network_reader(url: str) -> List[Dict]:
    analyzer = NetworkAnalyzer()
    return analyzer.analyze_url(url)

def main():
    parser = argparse.ArgumentParser(description='Analyze network requests for a given URL')
    parser.add_argument('url', nargs='?', default='https://suno.com/create', help='URL to analyze')
    parser.add_argument('--output', help='Output file path for JSON results')
    parser.add_argument('--no-headless', action='store_true', help='Run in non-headless mode')
    
    args = parser.parse_args()
    
    print(f"\nAnalyzing URL: {args.url}")
    analyzer = NetworkAnalyzer(headless=not args.no_headless)
    requests = analyzer.analyze_url(args.url)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(requests, f, indent=2)
        print(f"\nResults saved to {args.output}")
    else:
        print("\nDetailed requests:")
        print(json.dumps(requests, indent=2))

if __name__ == "__main__":
    main()