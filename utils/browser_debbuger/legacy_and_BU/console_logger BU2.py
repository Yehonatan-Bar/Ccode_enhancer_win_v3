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

def get_console_logs(url, kill_existing=True):
    logger.info(f"=== Starting console logging for URL: {url} ===")
    
    if kill_existing:
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
            '--remote-allow-origins=*',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-default-apps',
            '--disable-popup-blocking',
            '--disable-translate',
            '--disable-background-networking',
            '--disable-sync',
            '--metrics-recording-only',
            '--disable-prompt-on-repost',
            '--auto-open-devtools-for-tabs',
            f'--user-data-dir={user_data_dir}',
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
        max_retries = 10
        retry_count = 0
        debugger_url = None
        
        while retry_count < max_retries:
            try:
                response = requests.get(f'http://localhost:{debug_port}/json')
                pages = response.json()
                
                # Look specifically for the page target, not DevTools
                for page in pages:
                    if page.get('type') == 'page' and url in page.get('url', ''):
                        debugger_url = page['webSocketDebuggerUrl']
                        break
                
                if debugger_url:
                    break
                    
                retry_count += 1
                time.sleep(1)
            except requests.exceptions.RequestException:
                retry_count += 1
                time.sleep(1)

        if not debugger_url:
            raise Exception("Failed to get WebSocket debugger URL")

        # Modified WebSocket setup and handling
        console_messages = []
        ws = None
        
        def on_message(ws, message):
            try:
                data = json.loads(message)
                logger.debug(f"Received message type: {data.get('method')}")
                logger.debug(f"Full message: {json.dumps(data, indent=2)}")

                # Handle both console API calls and console messages
                if data.get('method') in ['Runtime.consoleAPICalled', 'Console.messageAdded']:
                    params = data.get('params', {})
                    
                    if data['method'] == 'Runtime.consoleAPICalled':
                        args = params.get('args', [])
                        msg_type = params.get('type', 'log')
                        
                        # Process each argument
                        messages = []
                        for arg in args:
                            if arg.get('type') == 'string':
                                messages.append(arg.get('value', ''))
                            elif arg.get('type') == 'object':
                                preview = arg.get('preview', {})
                                if preview.get('properties'):
                                    obj_desc = {p['name']: p['value'] for p in preview['properties']}
                                    messages.append(json.dumps(obj_desc))
                                else:
                                    messages.append(arg.get('description', 'Object'))
                            else:
                                messages.append(str(arg.get('value', '')))
                        
                        msg = ' '.join(str(m) for m in messages if m)
                        if msg:
                            formatted_msg = f"[{msg_type.upper()}] {msg}"
                            console_messages.append(formatted_msg)
                            logger.info(f"Console message captured: {formatted_msg}")
                            print(f">> {formatted_msg}")
                    
                    elif data['method'] == 'Console.messageAdded':
                        message = params.get('message', {})
                        msg_type = message.get('level', 'log')
                        msg = message.get('text', '')
                        if msg:
                            formatted_msg = f"[{msg_type.upper()}] {msg}"
                            console_messages.append(formatted_msg)
                            logger.info(f"Console message captured: {formatted_msg}")
                            print(f">> {formatted_msg}")

            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                logger.debug(f"Problematic message: {message}")

        def on_error(ws, error):
            logger.error(f"WebSocket error: {error}")

        def on_close(ws, close_status_code, close_msg):
            logger.debug(f"WebSocket closed: {close_status_code} - {close_msg}")

        def on_open(ws):
            logger.info("WebSocket connection established")
            enable_commands = [
                {'id': 1, 'method': 'Runtime.enable'},
                {'id': 2, 'method': 'Console.enable'},
                {'id': 3, 'method': 'Page.enable'},
                {
                    'id': 4,
                    'method': 'Runtime.setAsyncCallStackDepth',
                    'params': {'maxDepth': 32}
                },
                {
                    'id': 5,
                    'method': 'Console.setTimestampsEnabled',
                    'params': {'enabled': True}
                }
            ]
            
            for cmd in enable_commands:
                ws.send(json.dumps(cmd))
                logger.debug(f"Sent command: {cmd['method']}")

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

        # Increase wait time for page load
        logger.debug("Waiting for page to load and generate console messages...")
        time.sleep(10)  # Wait for initial page load
        
        # Reload the page to ensure we capture all console messages
        ws.send(json.dumps({'id': 100, 'method': 'Page.reload'}))
        time.sleep(5)  # Wait for reload to complete

        print("\nBrowser is open with DevTools. Press Enter when you've finished interacting with the page...")
        input()
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
        if input("Do you want to close the browser? (y/n): ").lower() != 'y':
            logger.info("Leaving browser open")
            return
        
        # Cleanup only if user wants to close
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