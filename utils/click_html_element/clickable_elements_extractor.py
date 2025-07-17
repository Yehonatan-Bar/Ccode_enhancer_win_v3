import os
import json
import logging
import sys
from bs4 import BeautifulSoup
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from logs.setup_logging import archive_existing_logs, setup_logging

# Determine the project root directory (3 levels up from this file)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load the configuration for logging from the project root
config_path = os.path.join(project_root, 'config.json')
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
except Exception as e:
    raise FileNotFoundError(f"Configuration file not found at {config_path}: {e}")

# Modify the log file name to match the current file's name without the .py extension
config['logging']['log_file'] = os.path.basename(__file__).replace('.py', '.log')

# Ensure that the logs directory exists
logs_dir = os.path.join(project_root, 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Setup logging using the project's logging configuration
logger = setup_logging(config, __file__)

# Helper function to log large messages in smaller chunks
def log_large_message(logger, message, level='debug', prefix=""):
    max_length = 1000  # Adjust threshold as needed
    if len(message) <= max_length:
        getattr(logger, level)(f"{prefix}{message}")
    else:
        getattr(logger, level)(f"{prefix} (Message length: {len(message)} exceeds limit, splitting into parts)")
        for index in range(0, len(message), max_length):
            part = message[index:index+max_length]
            getattr(logger, level)(f"{prefix} Part {index // max_length + 1}: {part}")

def extract_clickable_elements(html: str, display_info: dict = None, all_links: list = None) -> list:
    """
    Parses the provided HTML and returns a list of clickable elements.
    
    Args:
        html (str): The HTML content as a string.
        display_info (dict): Information about the display where the browser is running.
        all_links (list): List of all links found by Selenium with their text and href.
    
    Returns:
        list: A list of dictionaries representing clickable elements.
    """
    logger.info("=== Starting extraction of clickable elements from HTML ===")
    logger.info(f"HTML content length: {len(html) if html else 0}")
    if not html:
        logger.warning("HTML content is empty or None. No clickable elements can be extracted.")
        return []

    logger.info(f"Display info: {display_info}")
    logger.info(f"Number of Selenium-found links: {len(all_links) if all_links else 0}")
    
    # Log large HTML content using helper
    log_large_message(logger, html, prefix="Full HTML content: ")

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    logger.info("HTML parsed successfully using BeautifulSoup")
    
    # 1. Verify parser capabilities
    logger.info(f"BeautifulSoup parser in use: {soup.builder.NAME}")
    logger.info(f"Parser features: {soup.builder.features}")
    
    # 2. Verify actual parsed content
    logger.info("First 300 characters of parsed HTML:")
    logger.info(str(soup)[:300])
    
    # 3. Check for XML namespace issues
    logger.info(f"XML namespace present: {bool(soup.find(lambda tag: tag.prefix))}")
    
    # 4. Verify HTML encoding
    logger.info(f"Original encoding detected: {soup.original_encoding}")
    logger.info(f"Current encoding: {soup.encoding}")
    
    # 5. Check for JavaScript-rendered content
    script_tags = soup.find_all('script')
    logger.info(f"Number of <script> tags found: {len(script_tags)}")
    logger.info(f"Script src attributes: {[s.get('src') for s in script_tags[:3]]}")
    
    # 6. Check for iframes
    iframes = soup.find_all('iframe')
    logger.info(f"Number of iframes found: {len(iframes)}")
    logger.info(f"Iframe sources: {[iframe.get('src') for iframe in iframes[:3]]}")
    
    # New: Log parser being used and document structure
    logger.info(f"BeautifulSoup parser in use: {soup.builder.NAME}")
    logger.info(f"HTML contains <html> tag: {bool(soup.html)}")
    logger.info(f"HTML contains <head> tag: {bool(soup.head)}")
    logger.info(f"HTML contains <body> tag: {bool(soup.body)}")
    
    # Enhanced structure logging
    if soup.html:
        logger.info("HTML structure summary:")
        logger.info(f"Number of direct children in <html>: {len(list(soup.html.children))}")
        if soup.body:
            logger.info(f"Number of elements in <body>: {len(list(soup.body.find_all(True)))}")
            logger.info(f"First 3 elements in <body>: {list(soup.body.children)[:3]}")
    
    # Enhanced tag analysis
    all_tags = soup.find_all(True)
    logger.info(f"Total elements in parsed HTML: {len(all_tags)}")
    tag_counter = {}
    for tag in all_tags:
        tag_counter[tag.name] = tag_counter.get(tag.name, 0) + 1
    logger.info(f"Tag counts: {tag_counter}")
    
    clickable_elements = []

    # 1. Extract <a> and <button> elements
    logger.info("Extracting <a> and <button> elements")
    a_button_tags = soup.find_all(['a', 'button'])
    logger.info(f"Number of <a> and <button> tags found: {len(a_button_tags)}")
    for tag in a_button_tags:
        logger.debug(f"Processing tag: <{tag.name}>, attributes: {tag.attrs}")
        if tag.name == 'a':
            href = tag.get('href', '')
            if all_links:
                matching_links = [link for link in all_links if link.get('href') == href]
                if matching_links:
                    logger.debug(f"Found matching Selenium link for href: {href}")
                    tag_text = matching_links[0].get('text', tag.get_text(strip=True))
                else:
                    tag_text = tag.get_text(strip=True)
            else:
                tag_text = tag.get_text(strip=True)

            if not href:
                logger.debug("Skipping <a> tag without href attribute")
                continue

            logger.debug(
                f"Found clickable <a> tag: href='{href}', text before strip: '{tag.get_text()}', "
                f"text after strip: '{tag_text}', attributes: {tag.attrs}"
            )
            clickable_elements.append({
                "tag": tag.name,
                "attributes": tag.attrs,
                "text": tag_text,
                "href": href
            })
        else:  # button
            logger.debug(
                f"Found clickable <button> tag: text before strip: '{tag.get_text()}', "
                f"text after strip: '{tag.get_text(strip=True)}', attributes: {tag.attrs}"
            )
            clickable_elements.append({
                "tag": tag.name,
                "attributes": tag.attrs,
                "text": tag.get_text(strip=True)
            })
    
    # 2. Extract <input> elements with clickable types
    logger.info("Extracting <input> elements with clickable types")
    input_tags = soup.find_all('input')
    logger.info(f"Number of <input> tags found: {len(input_tags)}")
    for tag in input_tags:
        input_type = tag.get('type', '').lower()
        logger.debug(
            f"Processing <input> tag: type='{input_type}', value='{tag.get('value', '')}', attributes: {tag.attrs}"
        )
        if input_type in ['button', 'submit', 'reset', 'image']:
            logger.debug(
                f"Found clickable <input> tag with type '{input_type}', value attribute: '{tag.get('value', '')}'"
            )
            clickable_elements.append({
                "tag": tag.name,
                "attributes": tag.attrs,
                "text": tag.get('value', '')
            })
    
    # 3. Extract any elements that have an "onclick" attribute
    logger.info("Extracting elements with an 'onclick' attribute")
    onclick_tags = soup.find_all(attrs={"onclick": True})
    logger.info(f"Number of elements with an 'onclick' attribute found: {len(onclick_tags)}")
    for tag in onclick_tags:
        logger.debug(
            f"Processing tag with onclick attribute: tag='{tag.name}', attributes={tag.attrs}, "
            f"text before strip: '{tag.get_text()}', text after strip: '{tag.get_text(strip=True)}', "
            f"onclick attribute: '{tag.get('onclick')}'"
        )
        if not any(el["tag"] == tag.name and el["attributes"] == tag.attrs for el in clickable_elements):
            logger.debug(
                f"Found clickable element with onclick attribute: tag='{tag.name}', attributes={tag.attrs}, "
                f"text='{tag.get_text(strip=True)}'"
            )
            clickable_elements.append({
                "tag": tag.name,
                "attributes": tag.attrs,
                "text": tag.get_text(strip=True)
            })
    
    # 4. Extract elements with role="button"
    logger.info("Extracting elements with role='button'")
    role_button_tags = soup.find_all(attrs={"role": "button"})
    logger.info(f"Number of elements with role='button' found: {len(role_button_tags)}")
    for tag in role_button_tags:
        logger.debug(
            f"Processing tag with role='button': tag='{tag.name}', attributes={tag.attrs}, "
            f"text before strip: '{tag.get_text()}', text after strip: '{tag.get_text(strip=True)}'"
        )
        if not any(el["tag"] == tag.name and el["attributes"] == tag.attrs for el in clickable_elements):
            logger.debug(
                f"Found clickable element with role='button': tag='{tag.name}', attributes={tag.attrs}, "
                f"text='{tag.get_text(strip=True)}'"
            )
            clickable_elements.append({
                "tag": tag.name,
                "attributes": tag.attrs,
                "text": tag.get_text(strip=True)
            })
    
    # Add display position information if available
    if display_info:
        for element in clickable_elements:
            element["display_info"] = {
                "screen_width": display_info.get('width'),
                "screen_height": display_info.get('height'),
                "display_number": display_info.get('display_number'),
                "is_primary": display_info.get('is_primary')
            }
    
    logger.info(f"Extraction complete: Found {len(clickable_elements)} clickable elements.")
    return clickable_elements

if __name__ == "__main__":
    # Test the function using sample HTML content
    sample_html = """
    <html>
      <body>
          <a href="https://example.com">Example Link</a>
          <a>No Link</a>
          <button>Click Here</button>
          <input type="submit" value="Submit Form">
          <div onclick="alert('clicked')">Clickable Div</div>
          <span role="button">Span Button</span>
      </body>
    </html>
    """
    logger.info("Running extract_clickable_elements test from command line.")
    clickable = extract_clickable_elements(sample_html)
    print("Clickable Elements:")
    for element in clickable:
        print(element) 