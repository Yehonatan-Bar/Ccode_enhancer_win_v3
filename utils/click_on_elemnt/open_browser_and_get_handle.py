import os
import sys
import logging
import webbrowser
import time
import win32gui
import win32process
from datetime import datetime
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# If you have a logging utils module like in get_element_desc.py, import it here.
# Adjust the import path as appropriate for your project structure.
# For example:
# from utils.logging_utils import setup_logging_directory, setup_logger

# Placeholder stubs for setup_logging_directory and setup_logger 
# if you have a custom implementation. Remove or replace with your actual imports.
def setup_logging_directory():
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    return logs_dir

def setup_logger(name, log_file, level=logging.INFO, fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', console_out=True):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # File handler
    file_handler = logging.FileHandler(log_file, mode='a')
    file_formatter = logging.Formatter(fmt)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler
    if console_out:
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(fmt)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger

def find_browser_window(process_id: int, logger: logging.Logger):
    """
    Finds the top-level window handle corresponding to the given process_id.
    Returns the window handle (HWND) or None if not found.
    """
    logger.info(f"Attempting to find browser window for process ID: {process_id}")
    found_hwnd = None

    def callback(hwnd, pid_to_find):
        nonlocal found_hwnd
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            t_pid, _ = win32process.GetWindowThreadProcessId(hwnd)
            if t_pid == pid_to_find:
                found_hwnd = hwnd
                logger.debug(f"Found matching HWND: {found_hwnd} for process ID: {pid_to_find}")
                return False  # Stop enumeration
        return True  # Continue enumeration

    win32gui.EnumWindows(callback, process_id)
    if found_hwnd is None:
        logger.warning(f"No window found for process ID: {process_id}")
    return found_hwnd

def open_browser_and_get_handle(url, logger=None):
    """
    1. Opens the given URL in Chrome via Selenium.
    2. Returns a WebDriver instance (rather than a window handle).
    """
    # Setup logging
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    if logger is None:
        log_file = os.path.join(logs_dir, f"browser_automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        logger = setup_logger('browser_automation', log_file, level=logging.INFO)
    
    logger.info(f"Opening Chrome with Selenium for URL: {url}")

    # Configure Chrome
    options = Options()
    # options.add_argument('--headless')  # Uncomment if you prefer headless mode
    driver = webdriver.Chrome(options=options)

    # Navigate to the URL
    driver.get(url)
    time.sleep(2)  # Wait briefly for page load

    logger.info("Chrome opened successfully via Selenium")
    return driver

def _get_all_process_info():
    """
    Helper that enumerates all processes, returning a list of process information objects.
    Each object will have .dwProcessId, .exeFile, etc.
    """
    # Using psapi or wmi could be an alternative approach on Windows.
    # For brevity, let’s just show a placeholder usage of win32process.EnumProcesses()
    # A more thorough approach is needed for actual matching of the .exe paths.
    import win32process, win32api
    pids = win32process.EnumProcesses()
    process_info_list = []
    for pid in pids:
        try:
            hProcess = win32api.OpenProcess(0x0400 | 0x0010, False, pid)  # PROCESS_QUERY_INFORMATION | PROCESS_VM_READ
            exeFile = win32process.GetModuleFileNameEx(hProcess, 0)
            process_info_list.append(
                type("ProcessInfo", (), {"dwProcessId": pid, "exeFile": exeFile})
            )
            win32api.CloseHandle(hProcess)
        except Exception:
            pass
    return process_info_list

def _get_hwnd_for_pids(pids, logger=None):
    """
    From among all top-level windows, pick the window whose PID is in the provided pids list.
    The first matching window handle is returned.
    """
    hwnd_found = []

    def callback(hwnd, extra):
        tid, current_pid = win32process.GetWindowThreadProcessId(hwnd)
        # Only match if it's in our set of pids and it's visible.
        if current_pid in pids and win32gui.IsWindowVisible(hwnd):
            hwnd_found.append(hwnd)
            return False  # Stop enumeration once found.

    try:
        win32gui.EnumWindows(callback, None)
    except Exception as e:
        # For example, catch error 5 and log gracefully
        if logger:
            logger.error(f"Unable to enumerate windows. Check privileges. Error: {e}", exc_info=True)
        return None

    if hwnd_found:
        if logger:
            logger.info(f"Found window handle(s): {hwnd_found}")
        return hwnd_found[0]

    return None

def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python open_url.py <URL>")
        sys.exit(1)

    url_to_open = sys.argv[1]

    try:
        driver = open_browser_and_get_handle(url_to_open)
        if driver:
            print(f"Successfully opened browser for: {url_to_open}")
        else:
            print("Failed to open browser.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)
    finally:
        # Quit the driver if needed:
        if 'driver' in locals() and driver:
            driver.quit()

if __name__ == "__main__":
    main()