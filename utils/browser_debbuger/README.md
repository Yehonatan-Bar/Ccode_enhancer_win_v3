# Browser Debugger Tools

A collection of tools for debugging, analyzing, and monitoring web pages using Chrome DevTools Protocol (CDP) and Selenium WebDriver.

## Tools Overview

### 1. Console Logger (`console_logger.py`)

Captures and logs all browser console messages (logs, warnings, errors) from a webpage in real-time.

**Features:**
- Launches Chrome with remote debugging enabled
- Connects via WebSocket to Chrome DevTools Protocol
- Captures all console API calls and messages
- Supports different message types (log, warn, error, info)
- Filters duplicate messages automatically
- Interactive mode - keeps browser open for manual interaction

**Usage:**
```python
from console_logger import console_logger

# Basic usage
logs = console_logger('https://example.com')

# With existing Chrome kill (default)
logs = console_logger('https://example.com', kill_existing=True)
```

**Command Line:**
```bash
python console_logger.py
# Default URL: http://127.0.0.1:5000/
```

**Returns:**
- List of formatted console messages with type prefixes (e.g., `[LOG]`, `[ERROR]`, `[WARN]`)

**Use Cases:**
- Debug JavaScript errors on production sites
- Monitor console output during automated testing
- Capture third-party script messages
- Analyze client-side logging

### 2. Detailed URL Analyzer (`detailed_url_analyzer.py`)

Performs comprehensive analysis of a webpage including resources, network traffic, security, performance, and interactivity.

**Features:**
- Resource analysis (scripts, styles, images, fonts)
- Network traffic monitoring with request/response details
- Security header analysis and form inspection
- Performance metrics (timing, memory, paint events)
- Interactivity analysis (clickable elements, event listeners)
- Storage inspection (localStorage, sessionStorage)
- Saves detailed JSON report

**Usage:**
```python
from detailed_url_analyzer import DetailedURLAnalyzer

analyzer = DetailedURLAnalyzer(output_dir="analysis_results")
results = analyzer.analyze_url('https://example.com', wait_time=5)
```

**Command Line:**
```bash
python detailed_url_analyzer.py https://example.com
```

**Returns:**
- Comprehensive dictionary with analysis results
- Saves JSON file to `analysis_results/analysis_TIMESTAMP.json`

**Analysis Sections:**
1. **Basic Info**: URL, title, load time, domain
2. **Resources**: Scripts, stylesheets, images, fonts with metadata
3. **Network**: All requests, timing, domains, third-party tracking
4. **Security**: Headers, cookies, forms, external resources
5. **Performance**: Timing breakdown, memory usage, paint metrics
6. **Metadata**: Meta tags, headers structure
7. **Interactivity**: Clickable elements, event listeners, dynamic content
8. **Performance Metrics**: Detailed timing, resource timing, layout shifts

**Use Cases:**
- Website performance auditing
- Security assessment
- Resource optimization analysis
- Third-party dependency tracking
- SEO metadata inspection

### 3. Fetch Resource Details (`fetch_resource_details.py`)

Extracts detailed information about a specific resource request made by a webpage.

**Features:**
- Monitors all network requests via CDP
- Captures request headers and payload
- Captures response headers and body
- Supports all resource types (CSS, JS, API calls, images)
- Detailed request/response inspection

**Usage:**
```python
from fetch_resource_details import get_resource_details

get_resource_details('https://example.com', 'https://example.com/api/data')
```

**Command Line:**
```bash
python fetch_resource_details.py <page_url> <resource_url>
```

**Output:**
```
=== General Information ===
URL: https://example.com/api/data
Status: 200 OK
MIME Type: application/json

=== Request Headers ===
Accept: application/json
User-Agent: Mozilla/5.0...

=== Response Headers ===
Content-Type: application/json
Cache-Control: max-age=3600

=== Response Body ===
{"data": "example"}
```

**Use Cases:**
- Debug API calls and responses
- Inspect resource headers (caching, CORS)
- Analyze request payloads
- Troubleshoot failed resource loads

### 4. Get Page Resources (`get_page_resources.py`)

Simple tool to list all resource URLs requested by a webpage.

**Features:**
- Lists all network requests made by a page
- Filters out data: URLs
- Keeps browser open for inspection
- Simple resource discovery

**Usage:**
```python
from get_page_resources import get_page_resources

resources = get_page_resources('https://example.com')
for resource in resources:
    print(resource)
```

**Command Line:**
```bash
python get_page_resources.py
# Interactive prompt for URL
```

**Returns:**
- Sorted list of all unique resource URLs

**Use Cases:**
- Quick resource inventory
- Find all external dependencies
- Identify missing resources
- Prepare for offline analysis

## Requirements

- Python 3.7+
- Selenium WebDriver
- Chrome/Chromium browser
- ChromeDriver

## Installation

```bash
pip install selenium websocket-client requests
```

## Configuration

All tools use a `config.json` file for logging configuration. Ensure this file exists in the project root:

```json
{
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  }
}
```

## Logging

All tools use structured logging via the `setup_logging` utility. Logs include:
- Detailed execution flow
- Error tracking with stack traces
- Performance timing
- Resource discovery progress

## Common Parameters

- **URL**: Target webpage to analyze
- **wait_time**: Time to wait for dynamic content (default: 5 seconds)
- **output_dir**: Directory for saving results

## Error Handling

All tools include comprehensive error handling:
- WebDriver initialization failures
- Network timeouts
- Invalid URLs (auto-prefixed with https://)
- Chrome process management
- Resource not found scenarios

## Browser Management

- Tools can run in headless or visible mode
- Console Logger includes interactive mode
- Automatic Chrome process cleanup
- Debugging port configuration

## Performance Considerations

- Headless mode available for automation
- Configurable wait times
- Resource filtering to reduce noise
- Efficient log processing

## Security Notes

- These tools inspect client-side behavior only
- No credentials or authentication handling
- Safe for production site analysis
- Respects robots.txt implicitly via browser