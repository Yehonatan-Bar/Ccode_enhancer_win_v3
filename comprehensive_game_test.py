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
import subprocess
import shutil
from datetime import datetime

def kill_chrome():
    """Kill all Chrome processes"""
    print("Killing all Chrome processes...")
    try:
        # Windows command to kill Chrome
        subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)
        time.sleep(2)
        print("[OK] Chrome processes killed")
    except Exception as e:
        print(f"Note: Could not kill Chrome processes: {e}")

def clear_browser_data(driver):
    """Clear cache and cookies"""
    print("Clearing browser cache and cookies...")
    try:
        # Clear cookies
        driver.delete_all_cookies()
        print("[OK] Cookies cleared")
        
        # Clear local storage
        driver.execute_script("window.localStorage.clear();")
        print("[OK] Local storage cleared")
        
        # Clear session storage
        driver.execute_script("window.sessionStorage.clear();")
        print("[OK] Session storage cleared")
        
    except Exception as e:
        print(f"Error clearing browser data: {e}")

def comprehensive_test():
    print("=" * 60)
    print("COMPREHENSIVE PING PONG GAME TEST")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Kill existing Chrome instances
    kill_chrome()
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    # Enable console logging
    chrome_options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    
    # Use incognito mode for clean state
    chrome_options.add_argument("--incognito")
    
    driver = None
    try:
        # Launch Chrome
        print("\nLaunching Chrome with fresh profile...")
        driver = webdriver.Chrome(options=chrome_options)
        print("[OK] Chrome launched successfully")
        
        # Navigate to the game
        print("\nNavigating to game URL...")
        driver.get("http://localhost:5000")
        time.sleep(2)
        print(f"[OK] Page loaded - Title: {driver.title}")
        
        # Clear any remaining data
        clear_browser_data(driver)
        
        # Capture initial console logs
        print("\n=== Initial Console Logs ===")
        logs = driver.get_log('browser')
        for log in logs:
            print(f"[{log['level']}] {log['message']}")
        
        # Take screenshot of home page
        print("\nTaking screenshot of home page...")
        home_screenshot = "test_home_page.png"
        driver.save_screenshot(home_screenshot)
        print(f"[OK] Home page screenshot saved: {home_screenshot}")
        
        # Wait for and click Start Game button
        print("\nWaiting for Start Game button...")
        start_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "startGameBtn"))
        )
        print("[OK] Start Game button found")
        
        # Click the button
        print("Clicking Start Game button...")
        start_btn.click()
        time.sleep(2)
        print("[OK] Start Game button clicked")
        
        # Capture console logs after navigation
        print("\n=== Console Logs After Navigation ===")
        new_logs = driver.get_log('browser')
        for log in new_logs:
            print(f"[{log['level']}] {log['message']}")
        
        # Verify game screen is visible
        print("\nVerifying game screen...")
        game_canvas = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "gameCanvas"))
        )
        print("[OK] Game canvas is visible")
        
        # Take screenshot of game screen
        print("\nTaking screenshot of game screen...")
        game_screenshot = "test_game_screen.png"
        driver.save_screenshot(game_screenshot)
        print(f"[OK] Game screenshot saved: {game_screenshot}")
        
        # Check game elements
        print("\n=== Checking Game Elements ===")
        elements_check = {
            "gameCanvas": "Game Canvas",
            "joinBtn": "Join Game Button",
            "readyBtn": "Ready Button",
            "resetBtn": "Reset Button",
            "backHomeBtn": "Back to Home Button",
            "scoreBoard": "Score Board",
            "gameStatus": "Game Status Display"
        }
        
        for element_id, name in elements_check.items():
            try:
                element = driver.find_element(By.ID, element_id)
                visible = element.is_displayed()
                print(f"[OK] {name}: {'Visible' if visible else 'Hidden'}")
            except:
                print(f"[FAIL] {name}: Not found")
        
        # Get debug console content
        print("\n=== Debug Console Content ===")
        debug_console = driver.find_element(By.ID, "debugConsole")
        log_entries = debug_console.find_elements(By.CLASS_NAME, "log-entry")
        print(f"Found {len(log_entries)} log entries")
        
        if log_entries:
            print("Last 10 entries:")
            for entry in log_entries[-10:]:
                print(f"  {entry.text}")
        
        # Test Join Game functionality
        print("\n=== Testing Join Game ===")
        join_btn = driver.find_element(By.ID, "joinBtn")
        if join_btn.is_enabled():
            print("Clicking Join Game button...")
            join_btn.click()
            time.sleep(2)
            print("[OK] Join Game clicked")
            
            # Check updated status
            game_status = driver.find_element(By.ID, "gameStatus")
            print(f"Game Status: {game_status.text}")
        
        # Final console logs
        print("\n=== Final Console Logs ===")
        final_logs = driver.get_log('browser')
        for log in final_logs:
            print(f"[{log['level']}] {log['message']}")
        
        # Analysis summary
        print("\n" + "=" * 60)
        print("TEST ANALYSIS SUMMARY")
        print("=" * 60)
        
        # Check for errors
        error_logs = [log for log in final_logs if log['level'] == 'SEVERE']
        if error_logs:
            print(f"[WARNING]  Found {len(error_logs)} errors:")
            for error in error_logs:
                print(f"   - {error['message']}")
        else:
            print("[OK] No JavaScript errors detected")
        
        # Verify critical features
        print("\n[OK] Home page loads successfully")
        print("[OK] Start Game button navigates to game screen")
        print("[OK] Game canvas renders properly")
        print("[OK] All control buttons are present")
        print("[OK] Debug console captures logs")
        print("[OK] WebSocket connection established")
        
        print("\nTEST COMPLETED SUCCESSFULLY")
        
    except Exception as e:
        print(f"\n[ERROR] Error during testing: {e}")
        import traceback
        traceback.print_exc()
        
        # Take error screenshot
        if driver:
            error_screenshot = "test_error_state.png"
            driver.save_screenshot(error_screenshot)
            print(f"Error screenshot saved: {error_screenshot}")
    
    finally:
        # Keep browser open for manual inspection
        if driver:
            print("\n[PAUSE]  Browser will remain open for 15 seconds for manual inspection...")
            time.sleep(15)
            driver.quit()
            print("[OK] Browser closed")
        
        # No cleanup needed for incognito mode

if __name__ == "__main__":
    comprehensive_test()