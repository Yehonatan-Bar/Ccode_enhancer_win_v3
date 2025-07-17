# Browser Handler Tools

A comprehensive suite of tools for browser automation, web page analysis, and content processing using Selenium WebDriver and Chrome DevTools Protocol.

## Tools Overview

### 1. Browser Manager (`browser_manager.py`)

Core browser management functionality for Chrome automation with remote debugging support.

**Features:**
- Starts Chrome with remote debugging enabled
- Manages Chrome processes and instances
- Selenium WebDriver integration
- Window finding and focusing capabilities
- Persistent user profiles for debugging sessions

**Usage:**
```python
from browser_manager import BrowserManager

# Initialize browser manager
browser_manager = BrowserManager(debug_port="9222", headless=False)

# Start Chrome with debugging
if browser_manager.start_chrome_debugging():
    # Setup Selenium driver
    browser_manager.setup_selenium_driver()
    
    # Navigate to URL
    browser_manager.driver.get("https://example.com")
    
    # Find and focus window
    window_handle = browser_manager.find_browser_window("https://example.com")
    browser_manager.focus_window(window_handle)
```

**Key Methods:**
- `start_chrome_debugging()`: Launches Chrome with remote debugging
- `setup_selenium_driver()`: Initializes Selenium WebDriver
- `find_browser_window(url)`: Finds Chrome window by URL domain
- `focus_window(window_handle)`: Brings window to foreground

### 2. JS Fetcher (`js_fetcher.py`)

Fetches JavaScript files from web pages with support for relative and absolute URLs.

**Features:**
- Fetches JavaScript content from URLs
- Handles relative URL resolution
- Batch processing of multiple JS files
- Error handling for failed fetches

**Usage:**
```python
from js_fetcher import js_fetcher

# Fetch JavaScript files
js_contents = js_fetcher(
    window_handle=12345,
    base_url="https://example.com",
    js_urls=["main.js", "/static/vendor.js", "https://cdn.example.com/lib.js"]
)

# Results: {'main.js': '...content...', '/static/vendor.js': '...content...'}
```

### 3. Main Page Inspector (`main_page_inspector.py`)

Comprehensive web page analysis tool that combines multiple analysis techniques.

**Features:**
- Complete page analysis workflow
- Screenshot capture
- Network request monitoring
- JavaScript file detection
- JSON result export
- Window geometry tracking

**Usage:**
```python
from main_page_inspector import main_page_inspector

# Analyze a URL
results = main_page_inspector("https://example.com", wait_time=5)

# Results include:
# - screenshot_path: Path to captured screenshot
# - network_logs: All network requests
# - js_files: List of JavaScript files
# - window_rect: Window dimensions
# - status_code: HTTP status
```

**Command Line:**
```bash
python main_page_inspector.py https://example.com
```

**Output Structure:**
```json
{
  "url": "https://example.com",
  "status_code": 200,
  "window_title": "Example Domain",
  "window_rect": [0, 0, 1920, 1080],
  "screenshot_path": "screenshots/screenshot_1234567890.png",
  "js_files": ["main.js", "analytics.js"],
  "network_logs": [...]
}
```

### 4. Network Analyzer (`network_analyzer.py`)

Analyzes network requests from saved JSON files and fetches content for analysis.

**Features:**
- Loads network logs from JSON files
- Filters requests by HTTP method and file extension
- Fetches actual content from URLs
- Detailed request/response analysis
- Batch processing with configurable limits

**Usage:**
```python
from network_analyzer import network_analyzer

# Analyze network requests from JSON file
output_file = network_analyzer("website_analysis_20241124.json")

# Customized analysis
analyzer = RequestAnalyzer()
results = analyzer.analyze_requests(
    json_file="analysis.json",
    methods=['GET', 'POST'],
    extensions=['.json', '.js', '.html'],
    max_requests=10
)
```

**Analysis Results:**
- Request details (URL, method, headers, body)
- Response details (status, headers, content preview)
- Timing information
- Cookie data

### 5. Network Reader (`network_reader.py`)

Real-time network request monitoring during page load.

**Features:**
- Captures all network requests in real-time
- Groups requests by MIME type
- Performance log analysis
- Headless and visible browser modes
- Request timing information

**Usage:**
```python
from network_reader import network_reader

# Analyze network requests for a URL
requests = network_reader("https://example.com")

# Command line with options
analyzer = NetworkAnalyzer(headless=True)
requests = analyzer.analyze_url("https://example.com")
```

**Command Line:**
```bash
python network_reader.py https://example.com --output results.json --no-headless
```

**Request Format:**
```json
{
  "url": "https://example.com/api/data",
  "method": "GET",
  "type": "application/json",
  "status": 200,
  "timestamp": "2024-01-01 12:00:00.123456"
}
```

### 6. Screenshot Handler (`screenshot_handler.py`)

Advanced screenshot capture with window-specific targeting.

**Features:**
- Window-specific screenshot capture
- Integration with main_page_inspector results
- MSS library for efficient capture
- Automatic directory creation
- Timestamp-based naming

**Usage:**
```python
from screenshot_handler import ScreenshotHandler, take_screenshot

# Quick screenshot
result = take_screenshot(window_handle=12345, screenshot_dir="screenshots")

# Using inspector results
handler = ScreenshotHandler()
result = handler.capture_screenshot(inspector_results=inspector_results)

# Result: {'screenshot_path': 'screenshots/screenshot_20240101_120000.png', 
#          'window_rect': [0, 0, 1920, 1080]}
```

### 7. URL Analyzer (`url_analyzer.py`)

Combined URL analysis with screenshot and content fetching.

**Features:**
- Complete URL analysis workflow
- HTML parsing with BeautifulSoup
- HTTP header analysis
- JavaScript file extraction
- Window management
- Network log processing

**Usage:**
```python
# As a method (partial implementation shown)
result = url_analyzer(url="https://example.com", wait_time=5)

# Returns comprehensive analysis including:
# - Page content
# - Screenshots
# - Network logs
# - JavaScript files
# - HTTP headers
# - Window information
```

### 8. Vision Processor (`vision_processor.py`)

AI-powered image analysis using GROQ API with Llama vision models.

**Features:**
- Local image and URL support
- Base64 encoding for local files
- Customizable prompts and questions
- Temperature and token control
- Detailed logging

**Usage:**
```python
from vision_processor import process_image_with_vision

# Analyze local image
result = process_image_with_vision(
    image_path="screenshot.png",
    question="What text is visible in this image?"
)

# Analyze image from URL
result = process_image_with_vision(
    image_path="https://example.com/image.jpg",
    prompt="Describe the UI elements in this screenshot",
    is_url=True
)

# With custom API key
result = process_image_with_vision(
    image_path="screenshot.png",
    api_key="your-groq-api-key"
)
```

**Environment Setup:**
```bash
export GROQ_API_KEY="your-api-key"
```

## Requirements

- Python 3.7+
- Selenium WebDriver
- Chrome/Chromium browser
- ChromeDriver
- Additional dependencies:
  - `requests`
  - `beautifulsoup4`
  - `mss` (for screenshots)
  - `pywin32` (for Windows)
  - `groq` (for vision processing)
  - `Pillow` (for image processing)

## Installation

```bash
pip install selenium requests beautifulsoup4 mss pywin32 groq pillow
```

## Configuration

All tools use a `config.json` file for logging configuration:

```json
{
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_file": "browser_handler.log"
  }
}
```

## Common Use Cases

### 1. Complete Website Analysis
```python
from main_page_inspector import main_page_inspector
from vision_processor import process_image_with_vision

# Analyze website
results = main_page_inspector("https://example.com")

# Analyze screenshot with AI
description = process_image_with_vision(
    results['screenshot_path'],
    question="Describe the layout and content of this webpage"
)
```

### 2. Network Traffic Analysis
```python
from network_reader import NetworkAnalyzer

# Monitor real-time network traffic
analyzer = NetworkAnalyzer()
requests = analyzer.analyze_url("https://example.com")

# Filter specific request types
api_calls = [r for r in requests if 'api' in r['url']]
```

### 3. JavaScript Analysis
```python
from js_fetcher import js_fetcher
from main_page_inspector import main_page_inspector

# Get JS files from page
results = main_page_inspector("https://example.com")
js_contents = js_fetcher(
    window_handle=results['window_handle'],
    base_url="https://example.com",
    js_urls=results['js_files']
)
```

## Error Handling

All tools include comprehensive error handling:
- Chrome startup failures
- Network timeouts
- Invalid URLs
- Missing dependencies
- API failures (vision processor)
- Window not found scenarios

## Performance Considerations

- Use headless mode for automation
- Configure appropriate wait times
- Limit concurrent Chrome instances
- Clean up browser processes
- Cache network analysis results

## Security Notes

- Tools respect browser security policies
- No credential handling
- Safe for production site analysis
- API keys should be stored securely
- Network logs may contain sensitive data

## Logging

All tools use structured logging with configurable levels:
- INFO: General operation flow
- DEBUG: Detailed execution information
- WARNING: Non-critical issues
- ERROR: Operation failures
- CRITICAL: System failures

## Windows-Specific Features

- Window handle management
- Focus and maximize windows
- Screen region capture
- Process management