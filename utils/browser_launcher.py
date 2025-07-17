import sys
import os
import json
import time
import subprocess
import webbrowser
from typing import Dict, Any, Optional, List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class BrowserLauncher:
    """
    A script that accepts a URL as a parameter, opens the default browser at that URL,
    clears the cache and cookies, refreshes the browser, and returns browser elements
    and data for other scripts to use.
    """
    
    def __init__(self, debug_port: str = "9223"):
        self.debug_port = debug_port
        self.chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        self.driver = None
        self.chrome_process = None
        
    def launch_browser_with_url(self, url: str, clear_data: bool = True) -> Dict[str, Any]:
        """
        Launch browser with the specified URL and return browser elements and data.
        
        Args:
            url (str): The URL to open
            clear_data (bool): Whether to clear cache and cookies
            
        Returns:
            Dict containing browser elements and metadata
        """
        try:
            # Step 1: Start Chrome with debugging
            if not self._start_chrome_debugging():
                return {"error": "Failed to start Chrome with debugging"}
            
            # Step 2: Setup Selenium driver
            if not self._setup_selenium_driver():
                return {"error": "Failed to setup Selenium driver"}
            
            # Step 3: Navigate to URL
            print(f"Navigating to: {url}")
            self.driver.get(url)
            
            # Step 4: Clear cache and cookies if requested
            if clear_data:
                self._clear_browser_data()
            
            # Step 5: Refresh the browser
            print("Refreshing browser...")
            self.driver.refresh()
            
            # Step 6: Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Step 7: Extract browser elements and data
            browser_data = self._extract_browser_data()
            
            return browser_data
            
        except Exception as e:
            return {"error": f"Browser launch failed: {str(e)}"}
    
    def _start_chrome_debugging(self) -> bool:
        """Start Chrome with remote debugging enabled."""
        try:
            # Check if Chrome is already running with debugging
            import requests
            try:
                requests.get(f'http://localhost:{self.debug_port}/json/version', timeout=1)
                print(f"Chrome already running with debugging on port {self.debug_port}")
                return True
            except requests.exceptions.ConnectionError:
                pass
            
            # Start new Chrome instance
            user_data_dir = os.path.join(os.getcwd(), f"chrome_debug_profile_{self.debug_port}")
            os.makedirs(user_data_dir, exist_ok=True)
            
            cmd = [
                self.chrome_path,
                f'--remote-debugging-port={self.debug_port}',
                f'--user-data-dir={user_data_dir}',
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-extensions',
                '--disable-popup-blocking',
                '--disable-background-networking',
                '--disable-sync',
                '--disable-translate',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
            
            print(f"Starting Chrome with debugging on port {self.debug_port}")
            self.chrome_process = subprocess.Popen(cmd)
            
            # Wait for Chrome to start
            max_wait = 15
            start_time = time.time()
            while time.time() - start_time < max_wait:
                try:
                    requests.get(f'http://localhost:{self.debug_port}/json/version', timeout=1)
                    print(f"Chrome debugging ready on port {self.debug_port}")
                    return True
                except requests.exceptions.ConnectionError:
                    time.sleep(0.5)
            
            print(f"Failed to start Chrome debugging after {max_wait} seconds")
            return False
            
        except Exception as e:
            print(f"Error starting Chrome: {str(e)}")
            return False
    
    def _setup_selenium_driver(self) -> bool:
        """Initialize Selenium WebDriver."""
        try:
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", f"localhost:{self.debug_port}")
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
            
            self.driver = webdriver.Chrome(options=chrome_options)
            print("Selenium WebDriver initialized successfully")
            return True
            
        except Exception as e:
            print(f"Failed to initialize WebDriver: {str(e)}")
            return False
    
    def _clear_browser_data(self) -> None:
        """Clear browser cache and cookies."""
        try:
            print("Clearing browser data...")
            # Clear cookies
            self.driver.delete_all_cookies()
            
            # Clear cache via Chrome DevTools
            self.driver.execute_cdp_cmd('Network.clearBrowserCache', {})
            self.driver.execute_cdp_cmd('Network.clearBrowserCookies', {})
            
            print("Browser data cleared successfully")
            
        except Exception as e:
            print(f"Warning: Could not clear all browser data: {str(e)}")
    
    def _extract_browser_data(self) -> Dict[str, Any]:
        """Extract comprehensive browser elements and metadata for navigation."""
        try:
            # Get page metadata
            page_data = {
                "url": self.driver.current_url,
                "title": self.driver.title,
                "page_source": self.driver.page_source,
                "page_source_length": len(self.driver.page_source),
                "window_size": self.driver.get_window_size(),
                "cookies": self.driver.get_cookies(),
                "page_ready": self._check_page_ready()
            }
            
            # Get all clickable elements with enhanced data
            clickable_elements = []
            clickable_selectors = [
                'a', 'button', 'input[type="submit"]', 'input[type="button"]', 
                '[onclick]', '[role="button"]', '[tabindex]', 'select', 
                '[data-testid]', '[data-cy]', '.btn', '.button'
            ]
            
            for selector in clickable_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for i, element in enumerate(elements):
                    try:
                        if element.is_displayed() and element.is_enabled():
                            # Generate multiple selectors for robust element identification
                            selectors = self._generate_element_selectors(element)
                            
                            clickable_elements.append({
                                "index": i,
                                "tag": element.tag_name,
                                "text": element.text[:200] if element.text else "",
                                "inner_text": element.get_attribute("innerText")[:200] if element.get_attribute("innerText") else "",
                                "id": element.get_attribute("id"),
                                "class": element.get_attribute("class"),
                                "href": element.get_attribute("href"),
                                "role": element.get_attribute("role"),
                                "data_testid": element.get_attribute("data-testid"),
                                "data_cy": element.get_attribute("data-cy"),
                                "name": element.get_attribute("name"),
                                "value": element.get_attribute("value"),
                                "location": element.location,
                                "size": element.size,
                                "is_displayed": element.is_displayed(),
                                "is_enabled": element.is_enabled(),
                                "selectors": selectors,
                                "xpath": self._get_xpath(element),
                                "parent_info": self._get_parent_info(element)
                            })
                    except Exception as e:
                        print(f"Error processing clickable element: {e}")
                        continue
            
            # Get all input elements with enhanced data
            input_elements = []
            inputs = self.driver.find_elements(By.TAG_NAME, 'input')
            textareas = self.driver.find_elements(By.TAG_NAME, 'textarea')
            selects = self.driver.find_elements(By.TAG_NAME, 'select')
            
            for i, input_elem in enumerate(inputs + textareas + selects):
                try:
                    if input_elem.is_displayed():
                        selectors = self._generate_element_selectors(input_elem)
                        
                        input_elements.append({
                            "index": i,
                            "tag": input_elem.tag_name,
                            "type": input_elem.get_attribute("type"),
                            "name": input_elem.get_attribute("name"),
                            "id": input_elem.get_attribute("id"),
                            "class": input_elem.get_attribute("class"),
                            "placeholder": input_elem.get_attribute("placeholder"),
                            "value": input_elem.get_attribute("value"),
                            "required": input_elem.get_attribute("required"),
                            "disabled": input_elem.get_attribute("disabled"),
                            "readonly": input_elem.get_attribute("readonly"),
                            "maxlength": input_elem.get_attribute("maxlength"),
                            "pattern": input_elem.get_attribute("pattern"),
                            "location": input_elem.location,
                            "size": input_elem.size,
                            "is_displayed": input_elem.is_displayed(),
                            "is_enabled": input_elem.is_enabled(),
                            "selectors": selectors,
                            "xpath": self._get_xpath(input_elem),
                            "parent_info": self._get_parent_info(input_elem)
                        })
                except Exception as e:
                    print(f"Error processing input element: {e}")
                    continue
            
            # Get all images with enhanced data
            images = []
            img_elements = self.driver.find_elements(By.TAG_NAME, 'img')
            for i, img in enumerate(img_elements):
                try:
                    if img.is_displayed():
                        selectors = self._generate_element_selectors(img)
                        
                        images.append({
                            "index": i,
                            "src": img.get_attribute("src"),
                            "alt": img.get_attribute("alt"),
                            "title": img.get_attribute("title"),
                            "id": img.get_attribute("id"),
                            "class": img.get_attribute("class"),
                            "location": img.location,
                            "size": img.size,
                            "selectors": selectors,
                            "xpath": self._get_xpath(img),
                            "natural_width": img.get_attribute("naturalWidth"),
                            "natural_height": img.get_attribute("naturalHeight")
                        })
                except Exception as e:
                    print(f"Error processing image element: {e}")
                    continue
            
            # Get page structure and navigation context
            page_structure = self._analyze_page_structure()
            
            # Get all forms for form-based navigation
            forms = self._extract_forms()
            
            # Get navigation links and menus
            navigation = self._extract_navigation_elements()
            
            # Return comprehensive browser data
            return {
                "status": "success",
                "driver": self.driver,  # Return driver instance for other scripts
                "page_data": page_data,
                "clickable_elements": clickable_elements,
                "input_elements": input_elements,
                "images": images,
                "forms": forms,
                "navigation": navigation,
                "page_structure": page_structure,
                "element_count": {
                    "total_elements": len(self.driver.find_elements(By.CSS_SELECTOR, '*')),
                    "clickable": len(clickable_elements),
                    "inputs": len(input_elements),
                    "images": len(images),
                    "forms": len(forms),
                    "navigation_items": len(navigation)
                },
                "interaction_methods": {
                    "click_element": "Use selectors from element['selectors'] to click",
                    "fill_input": "Use selectors from input element to fill forms",
                    "navigate": "Use href from navigation elements or clickable elements",
                    "wait_for_element": "Use any selector to wait for element presence"
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to extract browser data: {str(e)}"}
    
    def _generate_element_selectors(self, element) -> Dict[str, str]:
        """Generate multiple selectors for robust element identification."""
        selectors = {}
        
        try:
            # ID selector (most reliable)
            if element.get_attribute("id"):
                selectors["id"] = f"#{element.get_attribute('id')}"
            
            # Class selector
            if element.get_attribute("class"):
                classes = element.get_attribute("class").split()
                selectors["class"] = f".{'.'.join(classes)}"
                # First class only for simpler selector
                if classes:
                    selectors["first_class"] = f".{classes[0]}"
            
            # Name selector
            if element.get_attribute("name"):
                selectors["name"] = f"[name='{element.get_attribute('name')}']"
            
            # Data attributes
            if element.get_attribute("data-testid"):
                selectors["data_testid"] = f"[data-testid='{element.get_attribute('data-testid')}']"
            if element.get_attribute("data-cy"):
                selectors["data_cy"] = f"[data-cy='{element.get_attribute('data-cy')}']"
            
            # Tag with text (for links and buttons)
            if element.text and element.tag_name in ['a', 'button', 'span', 'div']:
                text_clean = element.text.strip()[:50]  # Limit text length
                selectors["text"] = f"{element.tag_name}[text*='{text_clean}']"
            
            # Tag selector
            selectors["tag"] = element.tag_name
            
            # Href for links
            if element.get_attribute("href"):
                selectors["href"] = f"a[href='{element.get_attribute('href')}']"
            
            # Type for inputs
            if element.get_attribute("type"):
                selectors["type"] = f"input[type='{element.get_attribute('type')}']"
            
        except Exception as e:
            print(f"Error generating selectors: {e}")
        
        return selectors
    
    def _get_xpath(self, element) -> str:
        """Generate XPath for element."""
        try:
            return self.driver.execute_script(
                "function getXPath(element) {"
                "  if (element.id !== '') {"
                "    return '//*[@id=\"' + element.id + '\"]';"
                "  }"
                "  if (element === document.body) {"
                "    return '/html/body';"
                "  }"
                "  var ix = 0;"
                "  var siblings = element.parentNode.childNodes;"
                "  for (var i = 0; i < siblings.length; i++) {"
                "    var sibling = siblings[i];"
                "    if (sibling === element) {"
                "      return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';"
                "    }"
                "    if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {"
                "      ix++;"
                "    }"
                "  }"
                "}"
                "return getXPath(arguments[0]);", element
            )
        except:
            return ""
    
    def _get_parent_info(self, element) -> Dict[str, str]:
        """Get parent element information for context."""
        try:
            parent = element.find_element(By.XPATH, "..")
            return {
                "tag": parent.tag_name,
                "class": parent.get_attribute("class"),
                "id": parent.get_attribute("id")
            }
        except:
            return {}
    
    def _check_page_ready(self) -> bool:
        """Check if page is fully loaded."""
        try:
            return self.driver.execute_script("return document.readyState") == "complete"
        except:
            return False
    
    def _analyze_page_structure(self) -> Dict[str, Any]:
        """Analyze page structure for navigation context."""
        try:
            structure = {
                "has_header": bool(self.driver.find_elements(By.TAG_NAME, 'header')),
                "has_nav": bool(self.driver.find_elements(By.TAG_NAME, 'nav')),
                "has_footer": bool(self.driver.find_elements(By.TAG_NAME, 'footer')),
                "has_sidebar": bool(self.driver.find_elements(By.CSS_SELECTOR, '.sidebar, .side-nav, aside')),
                "has_main": bool(self.driver.find_elements(By.TAG_NAME, 'main')),
                "sections": len(self.driver.find_elements(By.TAG_NAME, 'section')),
                "articles": len(self.driver.find_elements(By.TAG_NAME, 'article')),
                "h1_count": len(self.driver.find_elements(By.TAG_NAME, 'h1')),
                "h2_count": len(self.driver.find_elements(By.TAG_NAME, 'h2')),
                "h3_count": len(self.driver.find_elements(By.TAG_NAME, 'h3'))
            }
            return structure
        except Exception as e:
            print(f"Error analyzing page structure: {e}")
            return {}
    
    def _extract_forms(self) -> List[Dict[str, Any]]:
        """Extract all forms with their inputs."""
        forms = []
        try:
            form_elements = self.driver.find_elements(By.TAG_NAME, 'form')
            for i, form in enumerate(form_elements):
                if form.is_displayed():
                    form_inputs = []
                    inputs = form.find_elements(By.CSS_SELECTOR, 'input, textarea, select')
                    for inp in inputs:
                        if inp.is_displayed():
                            form_inputs.append({
                                "tag": inp.tag_name,
                                "type": inp.get_attribute("type"),
                                "name": inp.get_attribute("name"),
                                "id": inp.get_attribute("id"),
                                "placeholder": inp.get_attribute("placeholder"),
                                "required": inp.get_attribute("required"),
                                "selectors": self._generate_element_selectors(inp)
                            })
                    
                    forms.append({
                        "index": i,
                        "action": form.get_attribute("action"),
                        "method": form.get_attribute("method"),
                        "id": form.get_attribute("id"),
                        "class": form.get_attribute("class"),
                        "inputs": form_inputs,
                        "selectors": self._generate_element_selectors(form)
                    })
        except Exception as e:
            print(f"Error extracting forms: {e}")
        return forms
    
    def _extract_navigation_elements(self) -> List[Dict[str, Any]]:
        """Extract navigation menus and links."""
        navigation = []
        try:
            nav_selectors = [
                'nav a', '.nav a', '.navbar a', '.menu a', 
                '.navigation a', 'header a', '.header a'
            ]
            
            for selector in nav_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        navigation.append({
                            "text": element.text[:100],
                            "href": element.get_attribute("href"),
                            "id": element.get_attribute("id"),
                            "class": element.get_attribute("class"),
                            "location": element.location,
                            "selectors": self._generate_element_selectors(element),
                            "parent_nav": selector
                        })
        except Exception as e:
            print(f"Error extracting navigation: {e}")
        return navigation
    
    def close(self) -> None:
        """Clean up resources."""
        try:
            if self.driver:
                self.driver.quit()
            if self.chrome_process:
                self.chrome_process.terminate()
                self.chrome_process.wait(timeout=5)
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")


def main():
    """Main function for command line usage."""
    if len(sys.argv) < 2:
        print("Usage: python browser_launcher.py <URL> [clear_data]")
        print("Example: python browser_launcher.py https://www.google.com true")
        sys.exit(1)
    
    url = sys.argv[1]
    clear_data = sys.argv[2].lower() == 'true' if len(sys.argv) > 2 else True
    
    launcher = BrowserLauncher()
    
    try:
        print(f"Launching browser with URL: {url}")
        result = launcher.launch_browser_with_url(url, clear_data)
        
        if "error" in result:
            print(f"Error: {result['error']}")
            sys.exit(1)
        
        print("Browser launched successfully!")
        print(f"Page title: {result['page_data']['title']}")
        print(f"Current URL: {result['page_data']['url']}")
        print(f"Page ready: {result['page_data']['page_ready']}")
        print(f"Clickable elements found: {result['element_count']['clickable']}")
        print(f"Input elements found: {result['element_count']['inputs']}")
        print(f"Images found: {result['element_count']['images']}")
        print(f"Forms found: {result['element_count']['forms']}")
        print(f"Navigation items found: {result['element_count']['navigation_items']}")
        
        print("\nPage Structure:")
        structure = result['page_structure']
        print(f"  Has header: {structure.get('has_header', False)}")
        print(f"  Has navigation: {structure.get('has_nav', False)}")
        print(f"  Has footer: {structure.get('has_footer', False)}")
        print(f"  Has sidebar: {structure.get('has_sidebar', False)}")
        print(f"  Sections: {structure.get('sections', 0)}")
        
        print("\nNavigation Data Available:")
        print("  - Detailed element selectors (ID, class, XPath, etc.)")
        print("  - Element interaction states (displayed, enabled)")
        print("  - Form structures with input mappings")
        print("  - Navigation menu hierarchies")
        print("  - Page source for content analysis")
        
        print("\nSample clickable elements:")
        for i, elem in enumerate(result['clickable_elements'][:3]):
            print(f"  Element {i+1}: {elem['tag']} - '{elem['text'][:50]}...' - ID: {elem['id']}")
            print(f"    Selectors: {list(elem['selectors'].keys())}")
        
        if result['forms']:
            print(f"\nSample form:")
            form = result['forms'][0]
            print(f"  Form action: {form['action']}")
            print(f"  Form inputs: {len(form['inputs'])}")
            for inp in form['inputs'][:2]:
                print(f"    Input: {inp['tag']} type={inp['type']} name={inp['name']}")
        
        # Keep browser open for other scripts to use
        print("\nBrowser is ready for other scripts to use.")
        print("Driver instance and comprehensive navigation data available.")
        
        # Keep the browser open
        print("\nPress Ctrl+C to close the browser and exit...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nClosing browser...")
        
        return result
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        launcher.close()


if __name__ == "__main__":
    main()