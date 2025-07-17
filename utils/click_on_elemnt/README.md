# Click On Element Tools

A collection of tools for browser automation, element identification, and interaction using Selenium WebDriver and AI-powered vision analysis.

## Tools Overview

### 1. Open Browser and Get Handle (`open_browser_and_get_handle.py`)

Opens a browser using Selenium WebDriver and manages browser instances.

**Features:**
- Chrome browser automation with Selenium
- Process ID tracking
- Window handle discovery
- Configurable Chrome options
- Automatic logging setup

**Usage:**
```python
from open_browser_and_get_handle import open_browser_and_get_handle

# Open browser and get driver instance
driver = open_browser_and_get_handle("https://example.com")

# Use the driver for automation
driver.find_element_by_id("submit").click()
driver.quit()
```

**Command Line:**
```bash
python open_browser_and_get_handle.py https://example.com
```

**Helper Functions:**
- `find_browser_window(process_id, logger)`: Finds window handle by process ID
- `_get_all_process_info()`: Enumerates all system processes
- `_get_hwnd_for_pids(pids, logger)`: Maps process IDs to window handles

### 2. Bring to Front and Screenshot (`bring_to_front_and_screenshot.py`)

Takes screenshots of web pages using Selenium's built-in capabilities.

**Features:**
- Selenium-based screenshot capture
- Browser window maximization
- Timestamp-based file naming
- Configurable screenshot directory
- Page load waiting

**Usage:**
```python
from bring_to_front_and_screenshot import bring_to_front_and_screenshot

# Capture screenshot of a URL
screenshot_path = bring_to_front_and_screenshot("https://example.com")
print(f"Screenshot saved: {screenshot_path}")
```

**Output:**
- Screenshots saved to `C:\scripts\screenshots\`
- Filename format: `browser_screenshot_YYYYMMDD_HHMMSS.png`

### 3. Click Element (`click_element.py`)

Automatically clicks elements on web pages by their ID with Chrome debugging support.

**Features:**
- Chrome remote debugging integration
- Automatic Chrome process management
- Element waiting with timeout
- Selenium WebDriver automation
- Detailed operation logging

**Usage:**
```python
from click_element import click_element

# Click element by ID
success = click_element(
    element_id="submit-button",
    url="https://example.com",
    timeout=10
)
```

**Command Line:**
```bash
python click_element.py submit-button https://example.com
```

**Process Flow:**
1. Kills existing Chrome instances
2. Starts Chrome with remote debugging (port 9222)
3. Connects via Selenium
4. Navigates to URL (if provided)
5. Waits for element to be clickable
6. Clicks the element

### 4. Get Element Description (`get_element_desc.py`)

Uses AI vision processing to analyze screenshots and describe specific elements.

**Features:**
- Integration with VisionProcessor
- Natural language element description
- Detailed visual analysis
- Comprehensive element reporting
- Custom prompt construction

**Usage:**
```python
from get_element_desc import get_element_desc

# Get AI description of an element
description = get_element_desc(
    screenshot_path="screenshot.png",
    textual_description="login button",
    request_full_description=custom_prompt,
    logger=logger
)
```

**Command Line:**
```bash
python get_element_desc.py "C:\screenshots\page.png" "linkedin button"
```

**Analysis Includes:**
1. Visual appearance (shape, design)
2. Text content
3. Colors
4. Relative size
5. Neighboring elements

### 5. Get Element ID (`get_element_id.py`)

Uses LLM to identify element selectors from HTML content based on descriptions.

**Features:**
- LLM-powered element identification
- Natural language processing
- CSS selector generation
- ID extraction from HTML
- Custom prompt support

**Usage:**
```python
from get_element_id import get_element_id

# Get element ID from description
element_id = get_element_id(
    element_description="the submit button",
    html_content=html_content,
    custom_prompt=optional_prompt
)
```

**Example:**
```python
html = """
<button id="submit-btn" class="primary-button">Submit Form</button>
"""
element_id = get_element_id("the submit button", html)
# Returns: "submit-btn"
```

### 6. Navigate and Screenshot (`navigate_and_screenshot.py`)

Combines browser opening and screenshot capture in a single workflow.

**Features:**
- Complete navigation workflow
- Window handle retrieval
- Screenshot automation
- Comprehensive logging
- Error handling

**Usage:**
```python
from navigate_and_screenshot import navigate_and_screenshot

# Navigate to URL and capture screenshot
navigate_and_screenshot("https://example.com")
```

**Command Line:**
```bash
python navigate_and_screenshot.py https://example.com
```

**Workflow:**
1. Opens URL in browser
2. Retrieves window handle
3. Brings window to front
4. Takes screenshot
5. Returns screenshot path

## Requirements

- Python 3.7+
- Selenium WebDriver
- Chrome browser
- ChromeDriver
- Windows OS (for win32gui/win32process)
- Additional dependencies:
  - `pyautogui`
  - `pywin32`
  - Vision processing dependencies (for get_element_desc)
  - LLM dependencies (for get_element_id)

## Installation

```bash
pip install selenium pyautogui pywin32
```

## Configuration

### Chrome Remote Debugging
The tools use Chrome remote debugging on port 9222:
```python
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
subprocess.Popen([chrome_path, "--remote-debugging-port=9222"])
```

### Logging
All tools use structured logging with customizable configuration:
```python
logger = setup_logger(
    name='tool_name',
    log_file='tool.log',
    level=logging.INFO,
    fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Screenshot Directory
Default screenshot location: `C:\scripts\screenshots\`

## Common Use Cases

### 1. Automated Form Submission
```python
# Open browser
driver = open_browser_and_get_handle("https://form-site.com")

# Click submit button
success = click_element("submit-btn", timeout=10)

# Take screenshot of result
screenshot = bring_to_front_and_screenshot("https://form-site.com/success")
```

### 2. Element Analysis Workflow
```python
# Navigate and screenshot
navigate_and_screenshot("https://example.com")

# Analyze element in screenshot
description = get_element_desc(
    "screenshot.png",
    "navigation menu",
    request_full_description,
    logger
)

# Get element ID from HTML
element_id = get_element_id("navigation menu", html_content)
```

### 3. AI-Powered Interaction
```python
# Get element description from screenshot
element_desc = get_element_desc(screenshot_path, "login button", prompt, logger)

# Identify element in HTML
element_id = get_element_id(element_desc, html_content)

# Click the identified element
click_element(element_id, url)
```

## Error Handling

All tools include comprehensive error handling:
- Chrome process management errors
- Element not found exceptions
- Timeout handling
- Window handle resolution failures
- Screenshot capture errors

## Windows-Specific Features

- Process enumeration
- Window handle management
- Chrome process control
- Multi-monitor support

## Performance Considerations

- Page load wait times (typically 2-5 seconds)
- Element wait timeouts (configurable)
- Chrome startup time
- Screenshot capture overhead

## Security Notes

- Chrome runs with remote debugging enabled
- No credential handling
- Safe for automated testing
- Respects website automation policies

## Debugging Tips

1. Check Chrome installation path
2. Verify ChromeDriver compatibility
3. Monitor log files for detailed errors
4. Ensure proper window focus for screenshots
5. Validate element IDs before clicking