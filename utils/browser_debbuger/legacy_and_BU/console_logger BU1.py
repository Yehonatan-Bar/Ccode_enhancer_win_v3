import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import platform
import subprocess
import json
import websocket
import requests
import time
import traceback
from urllib.parse import urlparse
from logs.setup_logging import setup_logging
#C:\Users\yonzb\OneDrive\Documents\Ai_Projects\AI_Agents\Test_Arena\text_analysis_dashboard_GPT\run.py
# Load config and setup logging
with open('config.json', 'r') as f:
    config = json.load(f)

logger = setup_logging(config, __file__)

def get_chrome_path():
    logger.debug("=== Getting Chrome Path ===")
    system = platform.system()
    logger.debug(f"Detected operating system: {system}")
    
    chrome_path = None
    if system == "Windows":
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    elif system == "Darwin":
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    else:
        chrome_path = "google-chrome"
    
    logger.info(f"Using Chrome path: {chrome_path}")
    logger.debug(f"Path exists: {os.path.exists(chrome_path)}")
    return chrome_path

def get_console_logs(url):
    logger.info(f"=== Starting console logging for URL: {url} ===")
    
    # Kill existing Chrome processes more thoroughly
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)
        time.sleep(3)
    except Exception as e:
        logger.debug(f"Failed to kill existing Chrome processes: {e}")

    # Create a unique user data directory in the temp folder
    user_data_dir = os.path.join(os.environ.get('TEMP', os.getcwd()), f'chrome-debug-{int(time.time())}')
    os.makedirs(user_data_dir, exist_ok=True)
    
    logger.debug(f"Created user data directory: {user_data_dir}")
    
    # Modified Chrome launch command
    chrome_path = get_chrome_path()
    debug_port = 9222
    
    try:
        chrome_process = subprocess.Popen([
            chrome_path,
            f'--remote-debugging-port={debug_port}',
            '--no-first-run',
            '--no-sandbox',
            '--disable-gpu',
            '--headless=new',
            f'--user-data-dir={user_data_dir}',  # Updated user data directory
            '--disable-extensions',
            '--disable-dev-shm-usage',
            '--disable-software-rasterizer',  # Added for stability
            '--disable-crash-reporter',       # Added for stability
            url
        ])
        
        # Increase initial wait time and add polling
        logger.debug("Waiting for Chrome to initialize...")
        max_init_attempts = 5
        for attempt in range(max_init_attempts):
            time.sleep(3)
            try:
                requests.get(f'http://localhost:{debug_port}', timeout=1)
                logger.debug("Chrome debugging port is responding")
                break
            except requests.exceptions.RequestException:
                logger.debug(f"Waiting for Chrome to start (attempt {attempt + 1}/{max_init_attempts})")
                if attempt == max_init_attempts - 1:
                    raise Exception("Chrome failed to start properly")

        # Add retry logic for getting debugger URL
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = requests.get(f'http://localhost:{debug_port}/json', timeout=5)
                break
            except requests.exceptions.ConnectionError:
                if attempt < max_retries - 1:
                    logger.debug(f"Retry {attempt + 1}/{max_retries} getting debugger URL")
                    time.sleep(retry_delay)
                else:
                    raise

        logger.debug(f"Chrome process ID: {chrome_process.pid}")
        
        # Wait for Chrome to start
        logger.debug("Waiting for Chrome to initialize...")
        time.sleep(4)
        
        # Get the WebSocket debugger URL
        logger.info("Fetching WebSocket debugger URL...")
        response = requests.get(f'http://localhost:{debug_port}/json')
        logger.debug(f"Debugger response status: {response.status_code}")
        logger.debug(f"Available pages: {len(response.json())}")
        
        debugger_url = None
        for page in response.json():
            if page['type'] == 'page':
                debugger_url = page['webSocketDebuggerUrl']
                logger.debug(f"Found debugger URL: {debugger_url}")
                break
        
        if not debugger_url:
            logger.error("Could not find debugging WebSocket URL")
            raise Exception("Could not find debugging WebSocket URL")
        
        # Modified WebSocket setup and handling
        console_messages = []
        ws = None
        
        def on_message(ws, message):
            logger.debug("Received WebSocket message")
            data = json.loads(message)
            if data.get('method') == 'Runtime.consoleAPICalled':
                msg = data['params']['args'][0]['value']
                logger.info(f"Console message captured: {msg[:200]}...")
                console_messages.append(msg)

        def on_error(ws, error):
            logger.error(f"WebSocket error: {error}")

        def on_close(ws, close_status_code, close_msg):
            logger.debug(f"WebSocket closed: {close_status_code} - {close_msg}")

        def on_open(ws):
            logger.info("WebSocket connection established")
            # Enable console logging
            ws.send(json.dumps({
                'id': 1,
                'method': 'Runtime.enable'
            }))

        # Connect to Chrome DevTools Protocol with all callbacks
        logger.info("Establishing WebSocket connection...")
        ws = websocket.WebSocketApp(
            debugger_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )

        # Run WebSocket connection in a separate thread with timeout
        import threading
        ws_thread = threading.Thread(target=lambda: ws.run_forever())
        ws_thread.daemon = True
        ws_thread.start()

        # Wait for WebSocket to connect
        connection_timeout = 10
        start_time = time.time()
        while not ws.sock or not ws.sock.connected:
            if time.time() - start_time > connection_timeout:
                raise Exception("WebSocket connection timeout")
            time.sleep(0.1)

        # Wait for console messages
        logger.debug("Waiting for console messages...")
        time.sleep(5)

        # Properly close WebSocket
        ws.close()
        logger.info(f"Captured {len(console_messages)} console messages")
        return console_messages

    except Exception as e:
        logger.error("=== Unexpected Error ===")
        logger.error(f"Failed to capture console logs")
        logger.debug(f"Error type: {type(e).__name__}")
        logger.debug(f"Error message: {str(e)}")
        logger.debug(f"Stack trace: {traceback.format_exc()}")
        if 'ws' in locals() and ws:
            ws.close()
        raise

    finally:
        # Cleanup
        logger.info("=== Cleaning up Chrome process ===")
        if 'chrome_process' in locals():
            chrome_process.terminate()
            logger.debug("Chrome process terminated")
            try:
                time.sleep(1)
                if os.path.exists(user_data_dir):
                    import shutil
                    shutil.rmtree(user_data_dir, ignore_errors=True)
                    logger.debug(f"Cleaned up user data directory: {user_data_dir}")
            except Exception as e:
                logger.debug(f"Failed to clean up user data directory: {e}")

if __name__ == '__main__':
    try:
        url = 'http://127.0.0.1:5000/'
        logger.info(f"Starting console logger for: {url}")
        logs = get_console_logs(url)
        print('\n'.join(logs))
    except Exception as e:
        logger.error(f"Main execution failed: {str(e)}")
        sys.exit(1)