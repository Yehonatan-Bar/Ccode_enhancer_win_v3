# Click HTML Element Tools

A comprehensive suite for automated web element interaction, combining browser automation, element identification, and click simulation with AI-powered element selection.

## Tools Overview

### 1. Browser Opener (`browser_opener.py`)

Opens Chrome browser with advanced configuration and element waiting capabilities.

**Features:**
- Chrome WebDriver initialization with performance logging
- Display detection for multi-monitor setups
- Element waiting with CSS and XPath selectors
- Link extraction from pages
- JavaScript execution support
- Detailed HTML content retrieval

**Usage:**
```python
from browser_opener import browser_opener

# Basic usage
html, display_info, driver, all_links = browser_opener(
    url="https://example.com",
    keep_browser_open=True
)

# With target element waiting
target_selector = {
    'css': 'button.submit',
    'xpath': '//button[@type="submit"]'
}
html, display_info, driver, all_links = browser_opener(
    url="https://example.com",
    target_element_selector=target_selector,
    wait_timeout=20,
    check_visibility=True
)
```

**Parameters:**
- `url`: Target URL to open
- `target_element_selector`: Dict with CSS/XPath selectors
- `keep_browser_open`: Keep browser instance alive
- `wait_timeout`: Maximum wait time in seconds
- `check_visibility`: Wait for element visibility vs presence

**Returns:**
- HTML content of the page
- Display information (monitor details)
- WebDriver instance (if keep_browser_open=True)
- List of all links found on the page

### 2. Click HTML Element (`click_html_element.py`)

Main orchestrator that combines all tools to perform intelligent element clicking.

**Features:**
- Complete click workflow automation
- Before/after screenshot capture
- AI-powered element identification
- HTML state tracking
- Error handling and logging

**Usage:**
```python
from click_html_element import click_element

# Click an element based on natural language prompt
html, display_info, driver, screenshot_path = click_element(
    url="https://example.com",
    is_first_click=True,
    prompt="Click the login button"
)
```

**Workflow:**
1. Opens browser and loads URL
2. Takes "before" screenshot
3. Identifies element using AI
4. Clicks the identified element
5. Takes "after" screenshot
6. Returns updated HTML and driver

### 3. Clickable Elements Extractor (`clickable_elements_extractor.py`)

Extracts all potentially clickable elements from HTML content.

**Features:**
- BeautifulSoup HTML parsing
- Multiple clickable element types detection
- Link text matching with Selenium data
- Display position information integration
- Comprehensive element attribute extraction

**Usage:**
```python
from clickable_elements_extractor import extract_clickable_elements

clickable_elements = extract_clickable_elements(
    html=html_content,
    display_info=display_info,
    all_links=selenium_links
)
```

**Detected Elements:**
- `<a>` tags with href
- `<button>` elements
- `<input>` with types: button, submit, reset, image
- Elements with `onclick` attributes
- Elements with `role="button"`

**Output Format:**
```json
{
    "tag": "button",
    "attributes": {"id": "submit-btn", "class": "primary"},
    "text": "Submit",
    "display_info": {
        "screen_width": 1920,
        "screen_height": 1080,
        "display_number": 1
    }
}
```

### 4. Element Clicker (`element_clicker.py`)

Performs the actual clicking of identified elements with robust error handling.

**Features:**
- CSS and XPath selector support
- Automatic scrolling to element
- Multiple exception handling
- State preservation on failure
- Updated HTML retrieval

**Usage:**
```python
from element_clicker import element_clicker

# Click using CSS selector
updated_html, outcome_message, driver = element_clicker(
    driver=driver,
    selector="button#submit"
)

# Click using XPath
updated_html, outcome_message, driver = element_clicker(
    driver=driver,
    selector="xpath://button[@id='submit']"
)
```

**Error Handling:**
- `NoSuchElementException`: Element not found
- `ElementNotInteractableException`: Element not clickable
- `ElementClickInterceptedException`: Click blocked
- `StaleElementReferenceException`: Element no longer valid

### 5. Element Identifier (`element_identifier.py`)

AI-powered element identification using LLM and conversation management.

**Features:**
- XML prompt template loading
- Clickable elements processing
- Chunk-based processing for large HTML
- Multi-attempt retry logic
- Fallback selector handling
- Integration with LLM Router

**Usage:**
```python
from element_identifier import construct_element_identifier_prompt

selector = construct_element_identifier_prompt(
    html=html_content,
    prompt="Click the login button",
    screenshot_path="screenshot.png",
    display_info=display_info,
    all_links=all_links
)
```

**Processing Logic:**
1. Extracts clickable elements from HTML
2. Constructs prompt using XML templates
3. Sends to LLM for element identification
4. Validates response with conversation manager
5. Returns CSS/XPath selector

### 6. Screenshot Taker (`screenshot_taker.py`)

Captures screenshots with automatic archiving and multi-monitor support.

**Features:**
- Before/after click screenshot organization
- Automatic archiving of existing screenshots
- Multi-monitor region capture
- Timestamp-based naming
- PyAutoGUI integration

**Usage:**
```python
from screenshot_taker import take_screenshot

# Before click screenshot
screenshot_path = take_screenshot(
    display_info=display_info,
    driver=driver,
    is_before=True
)

# After click screenshot
screenshot_path = take_screenshot(
    display_info=display_info,
    driver=driver,
    is_before=False
)
```

**Directory Structure:**
```
screenshots/
├── before_click/
├── after_click/
└── archives/
```

## Complete Workflow Example

```python
from click_html_element import click_element

# Perform intelligent click based on natural language
url = "https://shopping-site.com"
prompt = "Add the first product to cart"

html, display_info, driver, screenshot = click_element(
    url=url,
    is_first_click=True,
    prompt=prompt
)

if html:
    print("Click successful!")
    print(f"Screenshot saved: {screenshot}")
    
    # Perform another action
    html2, _, driver, screenshot2 = click_element(
        url=driver.current_url,
        is_first_click=False,
        prompt="Go to checkout"
    )
```

## Requirements

- Python 3.7+
- Selenium WebDriver
- Chrome/Chromium browser
- ChromeDriver (auto-installed via webdriver-manager)
- BeautifulSoup4
- PyAutoGUI
- screeninfo
- LLM integration (for element_identifier)

## Installation

```bash
pip install selenium beautifulsoup4 pyautogui screeninfo webdriver-manager
```

## Configuration

Uses `config.json` for logging configuration:

```json
{
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_file": "click_element.log"
  }
}
```

## Advanced Features

### Multi-Monitor Support
- Automatic display detection
- Window position tracking
- Display-specific screenshots

### Element Waiting Strategies
- Document ready state
- Element presence
- Element visibility
- Custom timeout configuration

### AI Integration
- Natural language element identification
- Context-aware selection
- Fallback mechanisms

### Error Recovery
- Retry logic for element identification
- Graceful failure handling
- State preservation

## Use Cases

1. **Automated Testing**
   - UI regression testing
   - User flow validation
   - Cross-browser testing

2. **Web Scraping**
   - Dynamic content interaction
   - Form submission
   - Navigation automation

3. **RPA (Robotic Process Automation)**
   - Repetitive task automation
   - Data entry
   - Report generation

4. **Accessibility Testing**
   - Clickable element verification
   - Navigation path testing

## Debugging

- HTML saved to `debug_html.html`
- Detailed logging for each operation
- Screenshot archives for history
- JSON output of clickable elements

## Performance Considerations

- 5-second wait after page load
- Configurable element wait timeouts
- Chunk processing for large HTML
- Efficient element extraction

## Security Notes

- No credential storage
- Safe element interaction
- Controlled browser automation
- Respects website policies