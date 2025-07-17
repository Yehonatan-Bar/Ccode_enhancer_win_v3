from datetime import datetime
import os
from win32gui import GetWindowRect
import mss
import logging
from typing import Optional, Dict

class ScreenshotHandler:
    def __init__(self, screenshot_dir: str = "screenshots"):
        self.screenshot_dir = screenshot_dir
        self.logger = logging.getLogger(__name__)
        
        # Create screenshot directory if it doesn't exist
        os.makedirs(screenshot_dir, exist_ok=True)

    def capture_screenshot(self, window_handle: int = None, inspector_results: Optional[Dict] = None) -> Optional[Dict]:
        """
        Capture screenshot of specific window.
        Can use either a window handle directly or results from main_page_inspector
        """
        try:
            if inspector_results:
                # Use window rectangle from inspector results if available
                window_rect = inspector_results.get('window_rect')
                if not window_rect:
                    self.logger.error("No window rectangle found in inspector results")
                    return None
            elif window_handle:
                # Get window rectangle from handle
                window_rect = GetWindowRect(window_handle)
            else:
                self.logger.error("Neither window handle nor inspector results provided")
                return None

            with mss.mss() as sct:
                monitor = {
                    "top": window_rect[1],
                    "left": window_rect[0],
                    "width": window_rect[2] - window_rect[0],
                    "height": window_rect[3] - window_rect[1]
                }
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = os.path.join(self.screenshot_dir, f"screenshot_{timestamp}.png")
                sct.shot(mon=-1, output=screenshot_path)
                
                return {
                    "screenshot_path": screenshot_path,
                    "window_rect": window_rect
                }
        except Exception as e:
            self.logger.error(f"Screenshot capture failed: {str(e)}")
            return None

    def screenshot_handler(self, inspector_results: Dict) -> Optional[Dict]:
        """
        Convenience method to capture screenshot using main_page_inspector results
        """
        return self.capture_screenshot(inspector_results=inspector_results)

def take_screenshot(window_handle: int = None, screenshot_dir: str = "screenshots") -> Optional[Dict]:
    """
    Utility function to quickly take a screenshot using ScreenshotHandler.
    
    Args:
        window_handle (int, optional): Window handle to capture. Defaults to None.
        screenshot_dir (str, optional): Directory to save screenshots. Defaults to "screenshots".
    
    Returns:
        Optional[Dict]: Dictionary containing screenshot path and window rectangle, or None if failed
    """
    screenshot_handler = ScreenshotHandler(screenshot_dir=screenshot_dir)
    return screenshot_handler.capture_screenshot(window_handle=window_handle)