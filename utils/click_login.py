import sys
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def click_login_element():
    """Connect to existing Chrome instance and click login element."""
    try:
        # Connect to existing Chrome instance
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "localhost:9223")
        
        driver = webdriver.Chrome(options=chrome_options)
        print("Connected to existing Chrome instance")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        print(f"Current URL: {driver.current_url}")
        
        # Try different selectors for login element
        login_selectors = [
            "button:contains('Log in')",
            "a:contains('Log in')",
            "[text*='Login']",
            "[text*='log in']",
            "button[text*='Login']",
            "a[text*='Login']",
            ".login",
            "#login",
            "[data-testid*='login']",
            "[class*='login']",
            "button[class*='login']",
            "a[href*='login']",
            "[role='button'][text*='login']"
        ]
        
        # First try to find login elements using various methods
        login_element = None
        
        # Method 1: Look for buttons with login text
        try:
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if button.is_displayed() and button.text and "log" in button.text.lower():
                    print(f"Found button with text: {button.text}")
                    login_element = button
                    break
        except Exception as e:
            print(f"Error checking buttons: {e}")
        
        # Method 2: Look for links with login text
        if not login_element:
            try:
                links = driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    if link.is_displayed() and link.text and "log" in link.text.lower():
                        print(f"Found link with text: {link.text}")
                        login_element = link
                        break
            except Exception as e:
                print(f"Error checking links: {e}")
        
        # Method 3: Look for any clickable element with login-related class or id
        if not login_element:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, "[class*='login'], [id*='login'], [data-testid*='login']")
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"Found element with login-related selector: {element.tag_name}")
                        login_element = element
                        break
            except Exception as e:
                print(f"Error checking login selectors: {e}")
        
        # Method 4: Look for elements with onclick or role=button
        if not login_element:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, "[onclick], [role='button']")
                for element in elements:
                    if element.is_displayed() and element.text and "log" in element.text.lower():
                        print(f"Found clickable element: {element.tag_name} - {element.text}")
                        login_element = element
                        break
            except Exception as e:
                print(f"Error checking clickable elements: {e}")
        
        if login_element:
            print(f"Clicking on login element: {login_element.tag_name}")
            print(f"Element text: {login_element.text}")
            print(f"Element location: {login_element.location}")
            
            # Scroll element into view
            driver.execute_script("arguments[0].scrollIntoView(true);", login_element)
            time.sleep(0.5)
            
            # Click the element
            login_element.click()
            print("Successfully clicked login element!")
            
            # Wait a bit to see if navigation occurs
            time.sleep(2)
            print(f"New URL: {driver.current_url}")
            
        else:
            print("Could not find login element on the page")
            print("Let me list all visible buttons and links:")
            
            # List all buttons
            print("\nVisible buttons:")
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for i, button in enumerate(buttons[:10]):  # Show first 10
                if button.is_displayed():
                    print(f"  Button {i}: '{button.text}' - ID: {button.get_attribute('id')} - Class: {button.get_attribute('class')}")
            
            # List all links
            print("\nVisible links:")
            links = driver.find_elements(By.TAG_NAME, "a")
            for i, link in enumerate(links[:10]):  # Show first 10
                if link.is_displayed():
                    print(f"  Link {i}: '{link.text}' - href: {link.get_attribute('href')}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    click_login_element()