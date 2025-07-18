import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils', 'click_html_element'))

from click_html_element import click_element
import time

def test_game_with_click_tool():
    print("=== Testing Ping Pong Game with Click Tool ===")
    
    # The URL of our game
    url = "http://localhost:5000"
    
    try:
        # Test 1: Click Join Game button
        print("\n1. Clicking 'Join Game' button...")
        result = click_element(url, "click the Join Game button")
        if result['status'] == 'success':
            print("✓ Successfully clicked Join Game button")
            print(f"  Element clicked: {result.get('element_description', 'N/A')}")
        else:
            print(f"✗ Failed to click Join Game: {result.get('message', 'Unknown error')}")
        
        time.sleep(2)
        
        # Test 2: Click Ready button
        print("\n2. Clicking 'Ready' button...")
        result = click_element(url, "click the Ready button")
        if result['status'] == 'success':
            print("✓ Successfully clicked Ready button")
            print(f"  Element clicked: {result.get('element_description', 'N/A')}")
        else:
            print(f"✗ Failed to click Ready: {result.get('message', 'Unknown error')}")
        
        time.sleep(2)
        
        # Test 3: Try to interact with game canvas
        print("\n3. Clicking on the game canvas...")
        result = click_element(url, "click on the game canvas in the center")
        if result['status'] == 'success':
            print("✓ Successfully clicked on canvas")
            print(f"  Element clicked: {result.get('element_description', 'N/A')}")
        else:
            print(f"✗ Failed to click canvas: {result.get('message', 'Unknown error')}")
        
        time.sleep(2)
        
        # Test 4: Click Reset Game button
        print("\n4. Clicking 'Reset Game' button...")
        result = click_element(url, "click the Reset Game button")
        if result['status'] == 'success':
            print("✓ Successfully clicked Reset Game button")
            print(f"  Element clicked: {result.get('element_description', 'N/A')}")
        else:
            print(f"✗ Failed to click Reset: {result.get('message', 'Unknown error')}")
        
        print("\n=== Test completed ===")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_game_with_click_tool()