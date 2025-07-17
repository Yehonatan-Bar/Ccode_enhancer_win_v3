import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Import the click_element function
from utils.click_html_element.click_html_element import click_element

def main():
    """Click the login element on ilands-frontend website."""
    url = "https://ilands-frontend.onrender.com/"
    prompt = "Click on the login button or link"
    
    print(f"Navigating to {url} and looking for login element...")
    
    # Use the click_element function
    html_content, display_info, driver, screenshot_path = click_element(
        url=url,
        is_first_click=True,
        prompt=prompt
    )
    
    if html_content:
        print("\nSuccessfully clicked the login element!")
        print(f"Current URL: {driver.current_url if driver else 'Unknown'}")
        if screenshot_path:
            print(f"Screenshot saved at: {screenshot_path}")
        
        # Keep browser open for user to continue
        if driver:
            print("\nBrowser is open. You can now interact with the login page.")
            input("Press Enter to close the browser...")
            driver.quit()
    else:
        print("\nFailed to click the login element.")
        print("The page might not have a login button, or it might be loaded dynamically.")

if __name__ == "__main__":
    main()