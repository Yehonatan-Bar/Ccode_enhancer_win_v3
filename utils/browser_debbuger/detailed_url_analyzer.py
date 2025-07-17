import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
import requests
from logs.setup_logging import setup_logging

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

class DetailedURLAnalyzer:
    def __init__(self, output_dir: str = "analysis_results"):
        self.output_dir = output_dir
        self.logger = setup_logging(config, 'detailed_url_analyzer')
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize Chrome options
        self.logger.debug("Setting up Chrome options")
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL', 'browser': 'ALL'})
        
        self.driver = None

    def _ensure_valid_url(self, url: str) -> str:
        """Ensure URL has a valid protocol prefix"""
        self.logger.debug(f"Validating URL: {url}")
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.logger.debug(f"Added https:// prefix. New URL: {url}")
        return url

    def analyze_url(self, url: str, wait_time: int = 5) -> Dict:
        """Perform detailed analysis of the URL and return comprehensive results."""
        self.logger.info(f"Starting analysis for URL: {url}")
        
        try:
            # Validate URL
            url = self._ensure_valid_url(url)
            self.logger.info(f"Using validated URL: {url}")
            
            # Initialize WebDriver with additional preferences
            self.chrome_options.add_argument('--enable-logging')
            self.chrome_options.add_argument('--v=1')  # Verbose logging
            self.chrome_options.add_experimental_option('perfLoggingPrefs', {
                'enableNetwork': True,
                'enablePage': True,
                'traceCategories': 'browser,content,devtools,network,renderer,timeline'
            })
            
            self.logger.debug("Initializing Chrome WebDriver")
            self.driver = webdriver.Chrome(options=self.chrome_options)
            
            # Create analysis timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.logger.debug(f"Analysis timestamp: {timestamp}")
            
            # Load the page
            self.logger.info(f"Loading URL in browser: {url}")
            start_time = time.time()
            self.driver.get(url)
            
            self.logger.debug(f"Waiting {wait_time} seconds for page load")
            time.sleep(wait_time)  # Wait for dynamic content
            
            load_time = time.time() - start_time
            self.logger.info(f"Page loaded in {load_time:.2f} seconds")
            
            # Collect detailed information
            self.logger.debug("Starting detailed information collection")
            
            analysis_results = {
                'basic_info': self._collect_basic_info(url, load_time, timestamp),
                'resources': self._analyze_resources(),
                'network': self._analyze_network_traffic(),
                'security': self._analyze_security(),
                'performance': self._analyze_performance(),
                'metadata': self._extract_metadata(),
                'interactivity': self._analyze_page_interactivity(),
                'performance_metrics': self._analyze_performance_metrics()
            }
            
            # Save results
            output_path = self._save_results(analysis_results, timestamp)
            analysis_results['output_path'] = output_path
            
            self.logger.info("Analysis completed successfully")
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error during analysis: {str(e)}", exc_info=True)
            raise
        finally:
            if self.driver:
                self.logger.debug("Closing WebDriver")
                self.driver.quit()

    def _collect_basic_info(self, url: str, load_time: float, timestamp: str) -> Dict:
        """Collect basic page information"""
        self.logger.debug("Collecting basic page information")
        return {
            'url': url,
            'title': self.driver.title,
            'load_time': round(load_time, 2),
            'timestamp': timestamp,
            'domain': urlparse(url).netloc
        }

    def _analyze_resources(self) -> Dict:
        """Analyze page resources"""
        self.logger.debug("Starting resource analysis")
        resources = {
            'scripts': [],
            'styles': [],
            'images': [],
            'fonts': [],
            'other': []
        }
        
        try:
            # Collect scripts
            self.logger.debug("Collecting script resources")
            scripts = self.driver.find_elements('tag name', 'script')
            for script in scripts:
                src = script.get_attribute('src')
                if src:
                    resources['scripts'].append({
                        'url': src,
                        'type': script.get_attribute('type') or 'text/javascript',
                        'async': script.get_attribute('async') is not None,
                        'defer': script.get_attribute('defer') is not None
                    })

            # Collect stylesheets
            self.logger.debug("Collecting stylesheet resources")
            styles = self.driver.find_elements('tag name', 'link')
            for style in styles:
                if style.get_attribute('rel') == 'stylesheet':
                    href = style.get_attribute('href')
                    if href:
                        resources['styles'].append({
                            'url': href,
                            'media': style.get_attribute('media') or 'all'
                        })

            # Collect images
            self.logger.debug("Collecting image resources")
            images = self.driver.find_elements('tag name', 'img')
            for img in images:
                src = img.get_attribute('src')
                if src:
                    resources['images'].append({
                        'url': src,
                        'alt': img.get_attribute('alt'),
                        'width': img.get_attribute('width'),
                        'height': img.get_attribute('height')
                    })

            # Also check background images in CSS
            self.logger.debug("Collecting background images")
            elements_with_bg = self.driver.execute_script("""
                return Array.from(document.getElementsByTagName('*')).filter(el => {
                    let style = window.getComputedStyle(el);
                    return style.backgroundImage && style.backgroundImage !== 'none';
                }).map(el => window.getComputedStyle(el).backgroundImage);
            """)
            
            for bg_img in elements_with_bg:
                if bg_img.startswith('url('):
                    url = bg_img.strip('url(").\')')
                    if url:
                        resources['images'].append({
                            'url': url,
                            'type': 'background-image'
                        })

            # Log resource counts
            for resource_type, items in resources.items():
                self.logger.info(f"Found {len(items)} {resource_type}")
            
        except Exception as e:
            self.logger.error(f"Error analyzing resources: {str(e)}", exc_info=True)
        
        return resources

    def _analyze_network_traffic(self) -> Dict:
        """Analyze network traffic and requests"""
        self.logger.debug("Starting network traffic analysis")
        network_info = {
            'requests': [],
            'timing_breakdown': {},
            'resource_types': {},
            'domains_contacted': set(),
            'third_party_requests': [],
            'largest_requests': []
        }
        
        try:
            logs = self.driver.get_log('performance')
            
            for entry in logs:
                try:
                    log = json.loads(entry['message'])['message']
                    
                    # Enhanced request tracking
                    if 'Network.requestWillBeSent' in log['method']:
                        params = log.get('params', {})
                        request = params.get('request', {})
                        
                        # Extract domain
                        domain = urlparse(request.get('url', '')).netloc
                        network_info['domains_contacted'].add(domain)
                        
                        request_data = {
                            'url': request.get('url'),
                            'method': request.get('method'),
                            'headers': request.get('headers', {}),
                            'timestamp': params.get('timestamp'),
                            'type': params.get('type', 'other'),
                            'request_id': params.get('requestId'),
                            'initiator': params.get('initiator', {}),
                            'resource_type': params.get('resourceType'),
                            'priority': params.get('priority'),
                            'is_third_party': domain != urlparse(self.driver.current_url).netloc
                        }
                        
                        network_info['requests'].append(request_data)
                        
                        # Track third-party requests
                        if request_data['is_third_party']:
                            network_info['third_party_requests'].append(request_data)
                        
                    # Track response data
                    elif 'Network.responseReceived' in log['method']:
                        params = log.get('params', {})
                        response = params.get('response', {})
                        
                        # Update resource type statistics
                        resource_type = params.get('type', 'other')
                        network_info['resource_types'][resource_type] = \
                            network_info['resource_types'].get(resource_type, 0) + 1
                        
                        # Track large responses
                        content_length = int(response.get('headers', {}).get('content-length', 0))
                        if content_length > 0:
                            network_info['largest_requests'].append({
                                'url': response.get('url'),
                                'size': content_length,
                                'type': resource_type
                            })
                
                except Exception as e:
                    self.logger.warning(f"Error processing network log entry: {str(e)}")
                    
            # Sort and limit largest requests
            network_info['largest_requests'].sort(key=lambda x: x['size'], reverse=True)
            network_info['largest_requests'] = network_info['largest_requests'][:10]
            
            # Convert domains set to list for JSON serialization
            network_info['domains_contacted'] = list(network_info['domains_contacted'])
            
            self.logger.info(f"Processed {len(network_info['requests'])} network requests")
            
        except Exception as e:
            self.logger.error(f"Error analyzing network traffic: {str(e)}")
            
        return network_info

    def _analyze_security(self) -> Dict:
        """Enhanced security analysis"""
        security_info = {
            'protocol': urlparse(self.driver.current_url).scheme,
            'cookies': self.driver.get_cookies(),
            'headers': {},
            'security_headers': {},
            'certificate_info': {},
            'form_analysis': [],
            'external_resources': [],
            'content_security_policy': None
        }
        
        try:
            # Get response headers
            response = requests.get(self.driver.current_url)
            security_info['headers'] = dict(response.headers)
            
            # Analyze security headers
            important_security_headers = [
                'Content-Security-Policy',
                'X-Frame-Options',
                'X-XSS-Protection',
                'X-Content-Type-Options',
                'Strict-Transport-Security',
                'Referrer-Policy'
            ]
            
            for header in important_security_headers:
                security_info['security_headers'][header] = response.headers.get(header)
            
            # Analyze forms
            forms = self.driver.find_elements('tag name', 'form')
            for form in forms:
                form_info = {
                    'action': form.get_attribute('action'),
                    'method': form.get_attribute('method'),
                    'has_csrf_token': bool(form.find_elements('css selector', 'input[name*=csrf]')),
                    'inputs': []
                }
                
                inputs = form.find_elements('tag name', 'input')
                for input_elem in inputs:
                    form_info['inputs'].append({
                        'type': input_elem.get_attribute('type'),
                        'name': input_elem.get_attribute('name'),
                        'has_autocomplete': input_elem.get_attribute('autocomplete') != 'off'
                    })
                
                security_info['form_analysis'].append(form_info)
            
            # Track external resources
            scripts = self.driver.find_elements('tag name', 'script')
            links = self.driver.find_elements('tag name', 'link')
            
            base_domain = urlparse(self.driver.current_url).netloc
            for element in scripts + links:
                src = element.get_attribute('src') or element.get_attribute('href')
                if src:
                    domain = urlparse(src).netloc
                    if domain and domain != base_domain:
                        security_info['external_resources'].append({
                            'url': src,
                            'type': element.tag_name,
                            'domain': domain
                        })
            
        except Exception as e:
            self.logger.error(f"Error in security analysis: {str(e)}")
        
        return security_info

    def _analyze_performance(self) -> Dict:
        """Analyze page performance metrics"""
        performance_metrics = self.driver.execute_script("""
            const performance = window.performance;
            const timing = performance.timing;
            return {
                navigationStart: timing.navigationStart,
                loadEventEnd: timing.loadEventEnd,
                domComplete: timing.domComplete,
                domInteractive: timing.domInteractive,
                domContentLoadedEventEnd: timing.domContentLoadedEventEnd
            }
        """)
        
        return performance_metrics

    def _extract_metadata(self) -> Dict:
        """Extract page metadata"""
        metadata = {
            'meta_tags': {},
            'links': [],
            'headers': []
        }
        
        # Extract meta tags
        meta_tags = self.driver.find_elements('tag name', 'meta')
        for meta in meta_tags:
            name = meta.get_attribute('name') or meta.get_attribute('property')
            if name:
                metadata['meta_tags'][name] = meta.get_attribute('content')

        # Extract headers
        headers = self.driver.find_elements('xpath', '//h1|//h2|//h3')
        for header in headers:
            metadata['headers'].append({
                'level': header.tag_name,
                'text': header.text
            })

        return metadata

    def _save_results(self, results: Dict, timestamp: str) -> str:
        """Save analysis results to file and return the full path"""
        try:
            filename = os.path.join(self.output_dir, f'analysis_{timestamp}.json')
            full_path = os.path.abspath(filename)
            self.logger.debug(f"Saving results to: {full_path}")
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Results successfully saved to {full_path}")
            return full_path
            
        except Exception as e:
            self.logger.error(f"Error saving results: {str(e)}", exc_info=True)
            raise

    def _analyze_page_interactivity(self) -> Dict:
        """Analyze interactive elements and dynamic behavior of the page"""
        self.logger.debug("Starting interactivity analysis")
        
        interactivity_info = {
            'clickable_elements': [],
            'event_listeners': [],
            'dynamic_content': [],
            'iframes': [],
            'websocket_connections': [],
            'ajax_endpoints': [],
            'local_storage': {},
            'session_storage': {}
        }
        
        try:
            # Analyze clickable elements
            clickable = self.driver.find_elements('css selector', 
                'button, a, input[type="button"], input[type="submit"], [onclick], [role="button"]')
            
            for element in clickable:
                # Convert WebElement to serializable dictionary
                element_info = {
                    'tag_name': element.tag_name,
                    'text': element.text,
                    'location': element.location,
                    'is_visible': element.is_displayed(),
                    'is_enabled': element.is_enabled(),
                    'attributes': {
                        'id': element.get_attribute('id'),
                        'class': element.get_attribute('class'),
                        'href': element.get_attribute('href'),
                        'onclick': element.get_attribute('onclick'),
                        'role': element.get_attribute('role')
                    }
                }
                interactivity_info['clickable_elements'].append(element_info)

            # Get event listeners using JavaScript
            event_listeners = self.driver.execute_script("""
                return Array.from(document.querySelectorAll('*')).map(element => {
                    const events = [];
                    const elementInfo = {
                        tag: element.tagName,
                        id: element.id,
                        class: element.className
                    };
                    
                    // Check for common event attributes
                    const eventAttributes = ['onclick', 'onmouseover', 'onmouseout', 
                        'onkeyup', 'onkeydown', 'onsubmit', 'onload'];
                    
                    eventAttributes.forEach(attr => {
                        if (element[attr]) {
                            events.push(attr.substring(2));
                        }
                    });
                    
                    if (events.length > 0) {
                        return {
                            element: elementInfo,
                            events: events
                        };
                    }
                    return null;
                }).filter(Boolean);
            """)
            interactivity_info['event_listeners'] = event_listeners

            # Analyze dynamic content
            dynamic_elements = self.driver.execute_script("""
                return Array.from(document.querySelectorAll('*')).filter(el => {
                    const style = window.getComputedStyle(el);
                    return style.animation !== 'none' || 
                           style.transition !== 'none' ||
                           el.getAttribute('data-*') !== null;
                }).map(el => ({
                    tag: el.tagName,
                    id: el.id,
                    class: el.className,
                    hasAnimation: window.getComputedStyle(el).animation !== 'none',
                    hasTransition: window.getComputedStyle(el).transition !== 'none',
                    dataAttributes: Object.keys(el.dataset)
                }));
            """)
            interactivity_info['dynamic_content'] = dynamic_elements

            # Analyze iframes
            iframes = self.driver.find_elements('tag name', 'iframe')
            for iframe in iframes:
                iframe_info = {
                    'src': iframe.get_attribute('src'),
                    'id': iframe.get_attribute('id'),
                    'name': iframe.get_attribute('name'),
                    'size': {
                        'width': iframe.get_attribute('width'),
                        'height': iframe.get_attribute('height')
                    }
                }
                interactivity_info['iframes'].append(iframe_info)

            # Check WebSocket connections
            websocket_info = self.driver.execute_script("""
                return performance.getEntriesByType('resource')
                    .filter(entry => entry.initiatorType === 'other' && 
                                    (entry.name.startsWith('ws://') || 
                                    entry.name.startsWith('wss://')))
                    .map(entry => ({
                        url: entry.name,
                        duration: entry.duration,
                        startTime: entry.startTime
                    }));
            """)
            interactivity_info['websocket_connections'] = websocket_info

            # Analyze AJAX endpoints
            ajax_info = self.driver.execute_script("""
                return performance.getEntriesByType('resource')
                    .filter(entry => entry.initiatorType === 'xmlhttprequest')
                    .map(entry => ({
                        url: entry.name,
                        duration: entry.duration,
                        startTime: entry.startTime,
                        method: entry.initiatorType
                    }));
            """)
            interactivity_info['ajax_endpoints'] = ajax_info

            # Get storage information
            interactivity_info['local_storage'] = self.driver.execute_script("""
                const storage = {};
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    storage[key] = localStorage.getItem(key);
                }
                return storage;
            """)

            interactivity_info['session_storage'] = self.driver.execute_script("""
                const storage = {};
                for (let i = 0; i < sessionStorage.length; i++) {
                    const key = sessionStorage.key(i);
                    storage[key] = sessionStorage.getItem(key);
                }
                return storage;
            """)

            return interactivity_info

        except Exception as e:
            self.logger.error(f"Error in interactivity analysis: {str(e)}")
            return interactivity_info

    def _analyze_performance_metrics(self) -> Dict:
        """Analyze detailed performance metrics"""
        self.logger.debug("Starting performance metrics analysis")
        
        performance_info = {
            'timing': {},
            'memory': {},
            'paint_metrics': [],
            'resource_timing': [],
            'layout_shifts': [],
            'long_tasks': [],
            'first_input_delay': None
        }
        
        try:
            # Get detailed timing metrics
            timing_metrics = self.driver.execute_script("""
                const t = performance.timing;
                return {
                    dns: t.domainLookupEnd - t.domainLookupStart,
                    tcp: t.connectEnd - t.connectStart,
                    ssl: t.connectEnd - t.secureConnectionStart,
                    ttfb: t.responseStart - t.requestStart,
                    download: t.responseEnd - t.responseStart,
                    dom_processing: t.domComplete - t.domLoading,
                    dom_interactive: t.domInteractive - t.navigationStart,
                    dom_content_loaded: t.domContentLoadedEventEnd - t.navigationStart,
                    load_complete: t.loadEventEnd - t.navigationStart
                };
            """)
            performance_info['timing'] = timing_metrics

            # Get memory usage
            memory_metrics = self.driver.execute_script("""
                const memory = performance.memory || {};
                return {
                    jsHeapSizeLimit: memory.jsHeapSizeLimit,
                    totalJSHeapSize: memory.totalJSHeapSize,
                    usedJSHeapSize: memory.usedJSHeapSize
                };
            """)
            performance_info['memory'] = memory_metrics

            # Get paint timing
            paint_metrics = self.driver.execute_script("""
                return performance.getEntriesByType('paint')
                    .map(entry => ({
                        name: entry.name,
                        startTime: entry.startTime
                    }));
            """)
            performance_info['paint_metrics'] = paint_metrics

            # Get resource timing
            resource_timing = self.driver.execute_script("""
                return performance.getEntriesByType('resource')
                    .map(entry => ({
                        name: entry.name,
                        initiatorType: entry.initiatorType,
                        duration: entry.duration,
                        transferSize: entry.transferSize,
                        encodedBodySize: entry.encodedBodySize,
                        decodedBodySize: entry.decodedBodySize
                    }));
            """)
            performance_info['resource_timing'] = resource_timing

            # Get layout shifts
            layout_shifts = self.driver.execute_script("""
                return performance.getEntriesByType('layout-shift')
                    .map(entry => ({
                        startTime: entry.startTime,
                        value: entry.value,
                        hadRecentInput: entry.hadRecentInput
                    }));
            """)
            performance_info['layout_shifts'] = layout_shifts

            # Get long tasks
            long_tasks = self.driver.execute_script("""
                return performance.getEntriesByType('longtask')
                    .map(entry => ({
                        startTime: entry.startTime,
                        duration: entry.duration,
                        name: entry.name
                    }));
            """)
            performance_info['long_tasks'] = long_tasks

            return performance_info

        except Exception as e:
            self.logger.error(f"Error in performance metrics analysis: {str(e)}")
            return performance_info
        
def detailed_url_analyzer(url: str) -> Dict:
    analyzer = DetailedURLAnalyzer()
    return analyzer.analyze_url(url)

def main():
    logger = setup_logging(config, 'detailed_url_analyzer')
    logger.info("Starting URL analyzer script")

    if len(sys.argv) != 2:
        logger.error("Invalid number of arguments")
        print("Usage: python detailed_url_analyzer.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    logger.info(f"Received URL for analysis: {url}")
    
    analyzer = DetailedURLAnalyzer()
    
    try:
        results = analyzer.analyze_url(url)
        
        print("\n=== Analysis Complete ===")
        print(f"Title: {results['basic_info']['title']}")
        print(f"Load Time: {results['basic_info']['load_time']}s")
        print(f"Scripts: {len(results['resources']['scripts'])}")
        print(f"Stylesheets: {len(results['resources']['styles'])}")
        print(f"Images: {len(results['resources']['images'])}")
        print(f"Network Requests: {len(results['network']['requests'])}")
        print(f"\nResults saved to: {results.get('output_path', 'Unknown path')}")
        
        logger.info("Script completed successfully")
        
    except Exception as e:
        logger.error(f"Script failed: {str(e)}", exc_info=True)
        print(f"Error analyzing URL: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()