# Browser Launcher

An advanced browser automation tool that launches Chrome with comprehensive element extraction and navigation data.

## Features

- Chrome browser automation with remote debugging
- Comprehensive element extraction (clickable, input, images, forms)
- Page structure analysis
- Navigation element identification
- Cache and cookie management
- Multi-selector generation for robust element identification
- Form detection and mapping
- Page readiness verification

## Usage

### Command Line
```bash
python browser_launcher.py <URL> [clear_data]

# Examples:
python browser_launcher.py https://www.google.com true
python browser_launcher.py https://example.com false
```

### As a Module
```python
from browser_launcher import BrowserLauncher

launcher = BrowserLauncher(debug_port="9223")
result = launcher.launch_browser_with_url("https://example.com", clear_data=True)

# Access the driver for further automation
driver = result['driver']

# Get clickable elements
for element in result['clickable_elements']:
    print(f"Element: {element['tag']} - {element['text']}")
    print(f"Selectors: {element['selectors']}")
```

## Return Data Structure

The tool returns a comprehensive dictionary containing:

### Page Data
- `url`: Current page URL
- `title`: Page title
- `page_source`: Complete HTML source
- `window_size`: Browser window dimensions
- `cookies`: All cookies
- `page_ready`: Page load status

### Element Collections
- `clickable_elements`: All clickable elements with multiple selectors
- `input_elements`: Form inputs, textareas, and selects
- `images`: All images with metadata
- `forms`: Complete form structures with inputs
- `navigation`: Navigation menus and links

### Page Analysis
- `page_structure`: Header, nav, footer, sidebar detection
- `element_count`: Summary of all element types
- `interaction_methods`: Guide for using the extracted data

## Element Selector Generation

Each element includes multiple selectors for robust identification:
- ID selector (most reliable)
- Class selectors (full and first class)
- Name attribute selector
- Data attributes (data-testid, data-cy)
- Text-based selectors
- XPath
- Type selectors (for inputs)

## Example Output

```python
{
    "status": "success",
    "driver": <selenium.webdriver.Chrome>,
    "page_data": {
        "url": "https://example.com",
        "title": "Example Domain",
        "page_ready": true
    },
    "clickable_elements": [
        {
            "tag": "button",
            "text": "Submit",
            "id": "submit-btn",
            "selectors": {
                "id": "#submit-btn",
                "class": ".btn.primary",
                "text": "button[text*='Submit']"
            },
            "xpath": "//button[@id='submit-btn']",
            "is_enabled": true
        }
    ],
    "element_count": {
        "clickable": 25,
        "inputs": 10,
        "forms": 2
    }
}
```

## Key Methods

- `launch_browser_with_url(url, clear_data)`: Main entry point
- `_clear_browser_data()`: Clears cache and cookies
- `_extract_browser_data()`: Comprehensive element extraction
- `_generate_element_selectors(element)`: Multi-selector generation
- `_analyze_page_structure()`: Page layout analysis
- `_extract_forms()`: Form structure extraction

## Use Cases

1. **Web Scraping**: Extract all interactive elements for automated data collection
2. **Test Automation**: Generate element selectors for test scripts
3. **Accessibility Analysis**: Analyze page structure and navigation
4. **Form Analysis**: Map complex forms for automated filling
5. **Navigation Mapping**: Extract site navigation structure

## Requirements

- Chrome browser
- ChromeDriver
- Python packages: selenium, requests

## Configuration

- Default debug port: 9223
- Chrome path: `C:\Program Files\Google\Chrome\Application\chrome.exe`
- User data stored in: `chrome_debug_profile_9223`