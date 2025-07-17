import os
import sys
import json
import logging
import screeninfo
from datetime import datetime
import traceback
import platform

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

if __name__ == '__main__':
    # When running directly
    import os
    import sys
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(project_root)
    from logs.setup_logging import archive_existing_logs, setup_logging
else:
    # When imported as a module
    try:
        from logs.setup_logging import archive_existing_logs, setup_logging
    except ImportError:
        # Fallback when imported from a different directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.append(project_root)
        from logs.setup_logging import archive_existing_logs, setup_logging

# Load the config
with open('config.json', 'r') as f:
    config = json.load(f)

# Modify the log file name
config['logging']['log_file'] = os.path.basename(__file__).replace('.py', '.log')

# Setup logging
logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(logs_dir, exist_ok=True)
logger = setup_logging(config, __file__)

def get_display_info():
    """
    Retrieves information about all connected monitors.
    
    Returns:
        list: A list of dictionaries containing information about each monitor.
    """
    logger.info("=== Starting display information retrieval ===")
    logger.debug(f"Process ID: {os.getpid()}")
    logger.debug(f"Current working directory: {os.getcwd()}")
    logger.debug(f"System info: {platform.platform()}")
    logger.debug(f"Python version: {sys.version}")
    
    try:
        # Get all connected monitors
        displays = screeninfo.get_monitors()
        logger.info(f"Number of displays detected: {len(displays)}")
        
        # Create a list to store display information
        display_info_list = []
        
        # Process each display
        for i, display in enumerate(displays):
            logger.debug(f"Processing display {i+1}: {display}")
            
            # Create a dictionary with display information
            display_info = {
                'display_number': i + 1,
                'width': display.width,
                'height': display.height,
                'x': display.x,
                'y': display.y,
                'is_primary': display.is_primary,
                'name': getattr(display, 'name', 'Unknown'),
                'dpi': getattr(display, 'dpi', 'Unknown')
            }
            
            logger.info(f"Display {i+1} info: {display_info}")
            display_info_list.append(display_info)
        
        # Save display information to a JSON file for reference
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(project_root, 'display_info')
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"display_info_{timestamp}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(display_info_list, f, indent=4)
        
        logger.info(f"Display information saved to: {output_file}")
        logger.info("=== Display information retrieval completed successfully ===")
        
        return display_info_list
        
    except Exception as e:
        logger.error("=== Error retrieving display information ===")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.debug(f"Error traceback: {traceback.format_exc()}")
        logger.debug(f"System info: {platform.platform()}")
        logger.debug(f"Python version: {sys.version}")
        return []

if __name__ == "__main__":
    # When run directly, print the display information
    display_info = get_display_info()
    
    if display_info:
        print("\n=== Display Information ===")
        for i, display in enumerate(display_info):
            print(f"\nDisplay {i+1}:")
            for key, value in display.items():
                print(f"  {key}: {value}")
    else:
        print("Failed to retrieve display information.")