import json
import requests
from typing import Dict, List, Optional
import logging
import os
from datetime import datetime
from urllib.parse import urlparse

class RequestAnalyzer:
    def __init__(self, log_dir: str = "RequestAnalyzer_logs"):
        self.logger = self.setup_logging(log_dir)

    def setup_logging(self, log_dir: str) -> logging.Logger:
        """Setup logging configuration"""
        os.makedirs(log_dir, exist_ok=True)
        logger = logging.getLogger(__name__)
        
        # Clear existing handlers
        if logger.handlers:
            logger.handlers.clear()
            
        log_file = os.path.join(log_dir, f'request_analyzer_{datetime.now().strftime("%Y%m%d")}.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.setLevel(logging.INFO)
        
        return logger

    def load_json_file(self, file_path: str) -> Optional[Dict]:
        """Load and parse JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading JSON file {file_path}: {str(e)}")
            return None

    def filter_network_calls(self, data: Dict, 
                           methods: List[str] = None, 
                           extensions: List[str] = None) -> List[Dict]:
        """Filter network calls based on methods and file extensions"""
        if not data or 'network_logs' not in data:
            return []

        filtered_calls = []
        methods = [m.upper() for m in (methods or ['GET', 'POST'])]
        extensions = extensions or ['.json', '.js', '.css', '.html']

        for call in data['network_logs']:
            url = call.get('url', '')
            method = call.get('method', '').upper()
            
            # Skip data: URLs
            if url.startswith('data:'):
                continue

            # Check if method matches
            if method not in methods:
                continue

            # Check extensions if specified
            if extensions:
                parsed_url = urlparse(url)
                path = parsed_url.path.lower()
                if not any(path.endswith(ext) for ext in extensions):
                    continue

            filtered_calls.append(call)

        return filtered_calls

    def fetch_url_content(self, url: str, headers: Dict = None, method: str = 'GET', data: Dict = None) -> Optional[Dict]:
        """Fetch headers and content from URL with full request/response details"""
        try:
            # Make the request
            response = requests.request(
                method=method,
                url=url,
                headers=headers or {},
                data=json.dumps(data) if data else None,
                timeout=10
            )
            
            return {
                'request': {
                    'url': url,
                    'method': method,
                    'headers': headers or {},
                    'body': data,
                    'timestamp': datetime.now().isoformat()
                },
                'response': {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'content': response.text[:1000],
                    'elapsed_time': response.elapsed.total_seconds(),
                    'encoding': response.encoding,
                    'cookies': dict(response.cookies)
                }
            }
        except Exception as e:
            self.logger.error(f"Error fetching URL {url}: {str(e)}")
            return None

    def analyze_requests(self, json_file: str, 
                        methods: List[str] = None,
                        extensions: List[str] = None,
                        max_requests: int = 5) -> List[Dict]:
        """Main method to analyze requests from JSON file"""
        self.logger.info(f"Analyzing requests from {json_file}")
        
        # Load JSON data
        data = self.load_json_file(json_file)
        if not data:
            return []

        # Filter network calls
        filtered_calls = self.filter_network_calls(data, methods, extensions)
        self.logger.info(f"Found {len(filtered_calls)} matching requests")

        # Fetch content for filtered calls (up to max_requests)
        results = []
        for call in filtered_calls[:max_requests]:
            url = call.get('url')
            if not url or url.startswith('data:'):
                continue
                
            self.logger.info(f"Fetching content for {url}")
            content = self.fetch_url_content(
                url=url,
                headers=call.get('headers', {}),
                method=call.get('method', 'GET'),
                data=call.get('body')
            )
            if content:
                results.append(content)

        return results

def network_analyzer(json_file_path: str) -> str:
    """
    Analyze network requests from a JSON file and save results
    
    Args:
        json_file_path (str): Path to the JSON file containing network logs
        
    Returns:
        str: Path to the output file containing analysis results
    """
    # Create output directory
    output_dir = "request_analysis_results"
    os.makedirs(output_dir, exist_ok=True)

    # Initialize analyzer
    analyzer = RequestAnalyzer()
    
    # Analyze requests
    results = analyzer.analyze_requests(
        json_file_path,
        methods=['GET'],
        extensions=['.json', '.js', '.html'],
        max_requests=5
    )

    # Save and return results
    if results:
        output_file = os.path.join(
            output_dir, 
            f"request_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        return output_file
    return ""

def main():
    json_file = "website_analysis_20241124_175407.json"  # Update with your file path
    result_path = network_analyzer(json_file)
    if result_path:
        print(f"\nResults saved to: {result_path}")
    else:
        print("No results found")

if __name__ == "__main__":
    main()