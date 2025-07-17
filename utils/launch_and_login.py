import sys
import os
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.browser_launcher import BrowserLauncher
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def launch_and_click_login():
    """Launch browser and click login element."""
    launcher = BrowserLauncher()
    
    try:
        print("Launching browser and navigating to ilands-frontend...")
        result = launcher.launch_browser_with_url("https://ilands-frontend.onrender.com/", clear_data=True)
        
        if "error" in result:
            print(f"Error: {result['error']}")
            return
        
        driver = result['driver']
        print("Browser launched successfully!")
        print(f"Current URL: {result['page_data']['url']}")
        
        # Wait a bit for any dynamic content to load
        time.sleep(3)
        
        # Look for login element in the clickable elements
        login_found = False
        for elem in result['clickable_elements']:
            text = (elem.get('text', '') + elem.get('inner_text', '')).lower()
            if 'log' in text or 'sign' in text:
                print(f"\nFound potential login element:")
                print(f"  Tag: {elem['tag']}")
                print(f"  Text: {elem.get('text', '')[:50]}")
                print(f"  ID: {elem.get('id', '')}")
                print(f"  Class: {elem.get('class', '')}")
                
                # Try to click using the best available selector
                try:
                    selectors = elem.get('selectors', {})
                    element = None
                    
                    # Try selectors in order of preference
                    if 'id' in selectors and selectors['id']:
                        element = driver.find_element(By.CSS_SELECTOR, selectors['id'])
                    elif 'data_testid' in selectors:
                        element = driver.find_element(By.CSS_SELECTOR, selectors['data_testid'])
                    elif 'class' in selectors:
                        element = driver.find_element(By.CSS_SELECTOR, selectors['class'])
                    elif 'xpath' in elem and elem['xpath']:
                        element = driver.find_element(By.XPATH, elem['xpath'])
                    
                    if element and element.is_displayed() and element.is_enabled():
                        # Scroll into view
                        driver.execute_script("arguments[0].scrollIntoView(true);", element)
                        time.sleep(0.5)
                        
                        # Click
                        element.click()
                        print("Successfully clicked login element!")
                        login_found = True
                        
                        # Wait to see if navigation occurs
                        time.sleep(3)
                        print(f"New URL: {driver.current_url}")
                        break
                        
                except Exception as e:
                    print(f"Could not click this element: {e}")
                    continue
        
        if not login_found:
            print("\nNo login element found. Here are all clickable elements with text:")
            for i, elem in enumerate(result['clickable_elements'][:20]):
                if elem.get('text') or elem.get('inner_text'):
                    text = elem.get('text', '') or elem.get('inner_text', '')
                    print(f"{i+1}. {elem['tag']} - '{text[:50]}' - ID: {elem.get('id', '')} - Class: {elem.get('class', '')[:50]}")
        
        # Keep browser open
        print("\nBrowser will remain open. Press Ctrl+C to close...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nClosing browser...")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        launcher.close()

if __name__ == "__main__":
    launch_and_click_login()