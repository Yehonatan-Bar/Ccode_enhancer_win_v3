import logging
import os
import sys
from datetime import datetime

# Point to the actual root directory of your project
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from utils.browser_handler.vision_processor import VisionProcessor
from utils.logging_utils import setup_logging_directory, setup_logger

def get_element_desc(screenshot_path: str, textual_description: str, request_full_description: str, logger: logging.Logger) -> str:
    """
    Combines the textual description and request for the element's details into a single prompt,
    sends it to the VisionProcessor, and returns the model's response.
    """
    logger.info("=== Starting element description analysis ===")
    logger.info(f"Screenshot path: {screenshot_path}")
    logger.info(f"Element description: {textual_description}")
    logger.debug(f"Additional request: {request_full_description}")

    try:
        vision_processor = VisionProcessor()
        logger.debug("VisionProcessor initialized successfully")

        # Construct the prompt
        prompt = (
            "Please analyze the following webpage screenshot and identify the element described below.\n\n"
            f"Screenshot path: {screenshot_path}\n\n"
            f"Element description: {textual_description}\n\n"
            f"Additional request: {request_full_description}\n\n"
            "Return a detailed description of how the element appears, including any relevant text, color, size, "
            "and its surrounding elements."
        )
        logger.debug(f"Constructed prompt: {prompt}")

        # Process the image and get the response
        logger.info("Processing image with VisionProcessor...")
        response = vision_processor.process_image(
            image_path=screenshot_path,
            question=prompt,
            is_url=False
        )
        logger.info("Image processing completed successfully")
        logger.debug(f"Vision model response: {response}")

        return response

    except Exception as e:
        logger.error("=== Error during element description analysis ===")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.debug(f"Traceback: {e.__traceback__}")
        raise

def main():
    """
    Main function of the script that sets up logging, defines the parameters for the
    request, and processes the element description.

    Usage (from cmd):
      python get_element_desc.py <screenshot_path> <textual_description>

    Example:
      python get_element_desc.py "C:\\Users\\yonzb\\OneDrive\\Documents\\Ai_Projects\\AI_Agents\\Tools_Hub\\screenshots\\1.png" "linkedin"
    """
    # Setup logging
    logs_dir = setup_logging_directory()
    log_file = os.path.join(
        logs_dir,
        f"element_desc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )

    logger = setup_logger(
        'element_desc',
        log_file,
        logging.INFO,
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        True
    )

    logger.info("=== Starting Element Description Script ===")

    # Command-line argument handling for screenshot_path and textual_description
    if len(sys.argv) < 3:
        print("Usage: python get_element_desc.py <screenshot_path> <textual_description>")
        sys.exit(1)

    screenshot_path = sys.argv[1]
    textual_description = sys.argv[2]

    # This request_full_description remains part of the script itself
    request_full_description = '''
      You are presented with a screenshot of a webpage or application. 
      Your task is to locate and provide a comprehensive description of a specific element based on the following criteria:

      Element Description: {textual_description}

      Please analyze the screenshot and provide a detailed description of the element that best matches this description. 
      Include the following details in your response:

      1. Appearance: Describe the visual characteristics of the element (e.g., shape, design).
      2. Text: If the element contains text, provide the exact text it contains.
      3. Color: Specify the colors present in the element.
      4. Size: Estimate the size of the element relative to the overall screenshot.
      5. Neighboring Elements: Describe the elements that are immediately adjacent to it. What is above, below, to the left, and to the right of this element?

      Your description should be as detailed as possible, enabling someone who has not seen the screenshot
      to understand precisely which element is being referred to and what it looks like.
    '''

    logger.info("Processing request with parameters:")
    logger.info(f"Screenshot path: {screenshot_path}")
    logger.info(f"Textual description: {textual_description}")
    logger.debug(f"Full description request: {request_full_description}")

    try:
        result = get_element_desc(
            screenshot_path,
            textual_description,
            request_full_description,
            logger
        )
        print("Model Response:")
        print(result)
        logger.info("Script completed successfully")
    except Exception as e:
        logger.error(f"Script failed with error: {str(e)}")
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 