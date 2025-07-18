import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import json

def test_ping_pong_game():
    print("=== Testing Ping Pong Game ===")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    # Enable console logging
    chrome_options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    
    try:
        # Launch Chrome
        driver = webdriver.Chrome(options=chrome_options)
        print("Chrome launched successfully")
        
        # Navigate to the game
        driver.get("http://localhost:5000")
        print(f"Navigated to game URL")
        
        # Wait for page to load
        time.sleep(2)
        
        # Get page title
        print(f"Page title: {driver.title}")
        
        # Extract console logs
        print("\n=== Console Logs ===")
        logs = driver.get_log('browser')
        for log in logs:
            print(f"[{log['level']}] {log['message']}")
        
        # Take a screenshot
        screenshot_path = "ping_pong_game_screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"\nScreenshot saved to: {screenshot_path}")
        
        # Find interactive elements
        print("\n=== Interactive Elements ===")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"Found {len(buttons)} buttons:")
        for button in buttons:
            print(f"  - {button.text} (enabled: {button.is_enabled()})")
        
        # Test Join Game button
        join_btn = driver.find_element(By.ID, "joinBtn")
        if join_btn.is_enabled():
            print("\nClicking 'Join Game' button...")
            join_btn.click()
            time.sleep(2)
            
            # Get updated console logs
            print("\n=== Console Logs After Join ===")
            new_logs = driver.get_log('browser')
            for log in new_logs:
                print(f"[{log['level']}] {log['message']}")
        
        # Check game status
        game_status = driver.find_element(By.ID, "gameStatus")
        print(f"\nGame Status: {game_status.text}")
        
        # Check debug console content
        print("\n=== Debug Console Content ===")
        debug_console = driver.find_element(By.ID, "debugConsole")
        log_entries = debug_console.find_elements(By.CLASS_NAME, "log-entry")
        print(f"Found {len(log_entries)} log entries in debug console")
        for entry in log_entries[-10:]:  # Last 10 entries
            print(f"  {entry.text}")
        
        # Keep browser open for manual testing
        print("\n=== Browser will stay open for 30 seconds for manual testing ===")
        print("You can interact with the game manually...")
        time.sleep(30)
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close browser
        driver.quit()
        print("\nBrowser closed")

if __name__ == "__main__":
    test_ping_pong_game()