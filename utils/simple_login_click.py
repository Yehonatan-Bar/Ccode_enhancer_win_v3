import sys
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.browser_launcher import BrowserLauncher

def main():
    """Launch browser and click login element on ilands-frontend."""
    launcher = BrowserLauncher()
    
    try:
        print("Launching browser and navigating to ilands-frontend...")
        result = launcher.launch_browser_with_url("https://ilands-frontend.onrender.com/", clear_data=True)
        
        if "error" in result:
            print(f"Error: {result['error']}")
            return
        
        driver = result['driver']
        print("Browser launched successfully!")
        
        # Wait for page to fully load
        time.sleep(5)
        
        # Try multiple approaches to find and click login
        login_clicked = False
        
        # Method 1: Look for text containing "log in" or "sign in"
        try:
            # Try different text variations
            login_texts = ["Log in", "Login", "Sign in", "Sign In", "LOG IN", "SIGN IN"]
            
            for text in login_texts:
                try:
                    # Try button with exact text
                    element = driver.find_element(By.XPATH, f"//button[text()='{text}']")
                    if element.is_displayed():
                        print(f"Found button with text: {text}")
                        element.click()
                        login_clicked = True
                        break
                except:
                    pass
                
                try:
                    # Try link with exact text
                    element = driver.find_element(By.XPATH, f"//a[text()='{text}']")
                    if element.is_displayed():
                        print(f"Found link with text: {text}")
                        element.click()
                        login_clicked = True
                        break
                except:
                    pass
                
                try:
                    # Try any element containing the text
                    element = driver.find_element(By.XPATH, f"//*[contains(text(), '{text}')]")
                    if element.is_displayed() and element.is_enabled():
                        print(f"Found element containing text: {text}")
                        element.click()
                        login_clicked = True
                        break
                except:
                    pass
        except Exception as e:
            print(f"Text search method failed: {e}")
        
        # Method 2: Look for login-related classes or IDs
        if not login_clicked:
            try:
                selectors = [
                    "button[class*='login']", "a[class*='login']", 
                    "button[id*='login']", "a[id*='login']",
                    "[class*='sign-in']", "[class*='signin']",
                    "button[class*='auth']", "a[class*='auth']"
                ]
                
                for selector in selectors:
                    try:
                        element = driver.find_element(By.CSS_SELECTOR, selector)
                        if element.is_displayed() and element.is_enabled():
                            print(f"Found element with selector: {selector}")
                            element.click()
                            login_clicked = True
                            break
                    except:
                        pass
            except Exception as e:
                print(f"Class/ID search method failed: {e}")
        
        # Method 3: Check all buttons and links
        if not login_clicked:
            print("\nChecking all visible buttons and links...")
            
            # Check buttons
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for i, button in enumerate(buttons):
                try:
                    if button.is_displayed() and button.text:
                        print(f"Button {i}: {button.text}")
                        if any(word in button.text.lower() for word in ['log', 'sign', 'auth']):
                            print(f"Clicking button: {button.text}")
                            button.click()
                            login_clicked = True
                            break
                except:
                    pass
            
            # Check links if no button found
            if not login_clicked:
                links = driver.find_elements(By.TAG_NAME, "a")
                for i, link in enumerate(links[:20]):  # Check first 20 links
                    try:
                        if link.is_displayed() and link.text:
                            print(f"Link {i}: {link.text}")
                            if any(word in link.text.lower() for word in ['log', 'sign', 'auth']):
                                print(f"Clicking link: {link.text}")
                                link.click()
                                login_clicked = True
                                break
                    except:
                        pass
        
        if login_clicked:
            print("\nSuccessfully clicked login element!")
            time.sleep(3)
            print(f"New URL: {driver.current_url}")
        else:
            print("\nCould not find login element on the page.")
            print("The page might be loading content dynamically or the login might be in a different format.")
        
        # Keep browser open
        print("\nBrowser will remain open. Press Enter to close...")
        input()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        launcher.close()

if __name__ == "__main__":
    main()