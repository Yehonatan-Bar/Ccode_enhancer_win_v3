# Claude Code Enhancer Windows v3

A comprehensive web automation and browser analysis toolkit with Claude AI integration, specifically designed for Windows environments.

## 🚀 Overview

This project provides a powerful suite of tools for web automation, browser debugging, network analysis, and AI-powered code enhancement. It integrates seamlessly with Claude AI to provide intelligent code review, analysis, and enhancement capabilities through role-based prompting.

## 📋 Table of Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Core Components](#-core-components)
- [Usage Examples](#-usage-examples)
- [Configuration](#-configuration)
- [API Reference](#-api-reference)
- [Contributing](#-contributing)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

## ✨ Features

### 🤖 Claude AI Integration
- **Role-based prompting** with 12+ predefined analysis roles
- **Git integration** for change tracking and diff analysis
- **Automated code review** with security, performance, and quality assessments
- **Cross-platform support** with Windows-optimized setup

### 🌐 Web Automation & Analysis
- **Browser automation** using Selenium WebDriver
- **Network traffic monitoring** and analysis
- **Resource extraction** (JavaScript, CSS, images, etc.)
- **Page performance analysis** and metrics collection
- **Security analysis** with vulnerability detection

### 🎯 Element Interaction
- **Smart element identification** using AI-powered analysis
- **Automated clicking** and interaction capabilities
- **Screenshot capture** and visual analysis
- **Multiple interaction strategies** for robust automation

### 🔍 Browser Debugging
- **Console logging** and error capture
- **Real-time debugging** with Chrome DevTools integration
- **Network request analysis** with detailed metrics
- **Resource loading optimization** insights

### 🖼️ Vision Processing
- **AI-powered image analysis** using Groq API
- **Screenshot processing** and analysis
- **Visual element recognition**
- **Multi-monitor support**

## 🔧 Prerequisites

### Required Software
- **Python 3.8+**
- **Google Chrome** (latest version)
- **Git for Windows** with Git Bash
- **Node.js** (for Claude CLI installation)

### Python Dependencies
```
selenium>=4.0.0
beautifulsoup4>=4.9.0
requests>=2.25.0
pygame>=2.0.0
pyautogui>=0.9.50
mss>=6.1.0
groq>=0.4.0
screeninfo>=0.6.0
webdriver-manager>=3.8.0
websocket-client>=1.0.0
pywin32>=300 (Windows only)
```

## 📦 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Ccode_enhancer_win_v3
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Claude CLI
```bash
npm install -g @anthropic-ai/claude-code
```

### 4. Setup Environment Variables
The script will automatically detect and configure:
- `CLAUDE_CODE_GIT_BASH_PATH` - Path to Git Bash executable
- `GROQ_API_KEY` - For vision processing (optional)

## 🚀 Quick Start

### Basic Claude Integration
```bash
# Simple prompt
python run_claude.py "analyze this codebase"

# Role-based analysis
python run_claude.py "security review" "check for vulnerabilities"

# Automated code review with multiple roles
python run_roles.py
```

### Automated Code Review System
The project includes a comprehensive automated code review system that analyzes your recent git commits through multiple specialized lenses. For detailed documentation, see [README_RUN_ROLES.md](README_RUN_ROLES.md).

Quick example:
```bash
# Run automated review with default configuration
python run_roles.py

# Run with custom delay and additional context
python run_roles.py --delay 5 --prompt "Focus on security aspects"
```

### Web Automation
```python
from utils.browser_handler.browser_manager import BrowserManager

# Initialize browser
browser = BrowserManager()
browser.start_chrome_debugging()

# Analyze a webpage
from utils.browser_handler.main_page_inspector import main_page_inspector
results = main_page_inspector("https://example.com")
```

### Element Interaction
```python
from utils.click_html_element.click_html_element import click_element

# Click an element on a webpage
result = click_element(
    url="https://example.com",
    is_first_click=True,
    prompt="Click the login button"
)
```

## 🏗️ Core Components

### 1. Claude AI Integration (`run_claude.py`, `run_roles.py`)
- **Multi-platform Claude CLI support**
- **Automated environment setup**
- **Git diff integration**
- **Role-based prompting system**
- **Interactive permission handling**
- **Automated Code Review System**: Comprehensive multi-role analysis of code changes with configurable severity levels. See [README_RUN_ROLES.md](README_RUN_ROLES.md) for detailed documentation.

### 2. Browser Handler (`utils/browser_handler/`)
- **`BrowserManager`**: Core browser automation and window management
- **`URLProcessor`**: Comprehensive webpage analysis
- **`NetworkAnalyzer`**: Network traffic analysis and monitoring
- **`ScreenshotHandler`**: Screenshot capture and management
- **`VisionProcessor`**: AI-powered image analysis

### 3. Browser Debugger (`utils/browser_debbuger/`)
- **`DetailedURLAnalyzer`**: In-depth webpage analysis
- **Console logging**: Real-time browser console monitoring
- **Resource analysis**: JavaScript, CSS, and asset inspection
- **Performance metrics**: Load times and optimization insights

### 4. Element Interaction (`utils/click_html_element/`, `utils/click_on_elemnt/`)
- **Smart element identification**: AI-powered element location
- **Multiple interaction strategies**: Robust clicking mechanisms
- **Visual confirmation**: Screenshot-based verification
- **Cross-browser compatibility**: Chrome and Edge support

### 5. Browser Launcher (`utils/browser_launcher.py`)
- **Enhanced navigation data extraction**: Comprehensive element metadata
- **Multiple selector strategies**: ID, class, XPath, data attributes
- **Interactive element states**: Displayed, enabled, clickable states
- **Form structure mapping**: Complete form and input relationships
- **Page structure analysis**: Headers, navigation, sections, sidebars
- **Navigation-ready data format**: Ready-to-use for automation scripts

### 6. Vision Processing (`utils/vision_processor/`)
- **Image analysis**: AI-powered image understanding
- **Screenshot processing**: Automated visual analysis
- **Multi-format support**: PNG, JPG, WebP compatibility

## 📚 Usage Examples

### Code Review Automation
```bash
# Run automated code review with configured roles
python run_roles.py

# Configure specific roles in roles_config.json then run
python run_roles.py --delay 5

# Custom prompt with single role
python run_claude.py "security review" "focus on authentication mechanisms"

# View git diff independently
python git_diff_last_commit.py
```

For comprehensive code review documentation and configuration options, see [README_RUN_ROLES.md](README_RUN_ROLES.md).

### Web Analysis Pipeline
```python
from utils.browser_handler.main_page_inspector import main_page_inspector
from utils.browser_handler.network_analyzer import network_analyzer

# Analyze webpage
results = main_page_inspector("https://example.com", wait_time=10)

# Analyze network traffic
network_data = network_analyzer("network_logs.json")
```

### Automated Testing
```python
from utils.click_html_element.click_html_element import click_element

# Test login flow
click_element("https://example.com/login", True, "click username field")
click_element("https://example.com/login", False, "click password field")
click_element("https://example.com/login", False, "click login button")
```

### Enhanced Browser Navigation
```python
from utils.browser_launcher import BrowserLauncher

# Launch browser with comprehensive navigation data
launcher = BrowserLauncher()
result = launcher.launch_browser_with_url('https://example.com')

# Access driver and navigation data
driver = result['driver']
clickable_elements = result['clickable_elements']
forms = result['forms']
navigation = result['navigation']

# Navigate using multiple selector strategies
for element in clickable_elements:
    selectors = element['selectors']
    # Try ID selector first (most reliable)
    if 'id' in selectors:
        driver.find_element(By.CSS_SELECTOR, selectors['id']).click()
    # Fall back to other selectors
    elif 'data_testid' in selectors:
        driver.find_element(By.CSS_SELECTOR, selectors['data_testid']).click()
    elif 'xpath' in element:
        driver.find_element(By.XPATH, element['xpath']).click()

# Fill forms with detailed input mapping
for form in forms:
    for input_elem in form['inputs']:
        if input_elem['type'] == 'email':
            selector = input_elem['selectors'].get('id') or input_elem['selectors'].get('name')
            driver.find_element(By.CSS_SELECTOR, selector).send_keys('test@example.com')
```

## ⚙️ Configuration

### Prompt Library (`prompt_library.xml`)
Customize AI analysis roles:
```xml
<roles>
    <prompt key="custom_role">Your custom analysis prompt here</prompt>
</roles>
```

### Available Analysis Roles
The automated code review system supports 16 specialized analysis roles with configurable severity levels (Critical, Standard, Best Practice):

- **Error Handling**: Exception handling and error scenarios
- **Security Review**: Vulnerability assessment and security best practices
- **Performance Review**: Optimization and efficiency analysis
- **Code Quality**: Maintainability and best practices
- **Testing Coverage**: Test completeness and strategy
- **Dependency Audit**: Package security and version management
- **API Design**: Interface design and usability
- **Logging Monitoring**: Observability and debugging capabilities
- **Data Validation**: Input/output validation and sanitization
- **Concurrency Review**: Thread safety and synchronization
- **Deployment Readiness**: Production deployment preparation
- **Accessibility Compliance**: WCAG standards and usability
- **Logging Implementation**: Consistency with existing logging patterns
- **Requirement Fulfillment**: Verification against original requirements
- **Integration Compatibility**: System integration and compatibility checks
- **State and Data Flow**: Data flow analysis and state management

Configure active roles and severity levels in `roles_config.json`. See [README_RUN_ROLES.md](README_RUN_ROLES.md) for detailed configuration.

### Environment Configuration
The system automatically configures:
- Chrome debugging port (default: 9222)
- Screenshot directories
- Log file locations
- Git Bash integration

## 📖 API Reference

### Core Classes

#### `BrowserManager`
```python
class BrowserManager:
    def __init__(self, debug_port="9222", headless=False)
    def start_chrome_debugging(self) -> bool
    def setup_selenium_driver(self)
    def find_browser_window(self, url: str) -> Optional[int]
    def focus_window(self, window_handle: int) -> bool
```

#### `URLProcessor`
```python
class URLProcessor:
    def __init__(self, screenshot_dir="screenshots")
    def analyze_url(self, url: str, wait_time: int = 5) -> Optional[Dict[str, Any]]
    def process_network_logs(self, driver)
    def get_js_files(self, driver) -> List[str]
```

#### `DetailedURLAnalyzer`
```python
class DetailedURLAnalyzer:
    def __init__(self, output_dir="analysis_results")
    def analyze_url(self, url: str, wait_time: int = 5) -> Dict
    def _analyze_security(self) -> Dict
    def _analyze_performance(self) -> Dict
```

### Utility Functions

#### Claude Integration
```python
def run_claude_windows(prompt, skip_permissions=False, timeout=300)
def load_prompts_from_xml(role)
def get_git_diff()
```

#### Web Automation
```python
def main_page_inspector(url: str, wait_time: int = 5) -> Optional[Dict[str, Any]]
def click_element(url: str, is_first_click: bool, prompt: str) -> Tuple
def network_analyzer(json_file_path: str) -> str
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Install development dependencies: `pip install -r requirements-dev.txt`
4. Make your changes following the coding standards
5. Run tests: `python -m pytest`
6. Submit a pull request

### Coding Standards
- **Python PEP 8** compliance
- **Comprehensive logging** for all operations
- **Error handling** for all external dependencies
- **Type hints** for function parameters and returns
- **Docstrings** for all classes and functions

### Testing Guidelines
- Unit tests for core functionality
- Integration tests for browser automation
- Visual tests for screenshot capabilities
- Performance benchmarks for analysis tools

## 🛠️ Troubleshooting

### Common Issues

#### Claude CLI Not Found
```bash
# Install Claude CLI
npm install -g @anthropic-ai/claude-code

# Verify installation
claude --version

# Check PATH configuration
echo $PATH
```

#### Chrome WebDriver Issues
```python
# Update ChromeDriver
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(ChromeDriverManager().install())
```

#### Git Bash Path Issues
The script automatically detects Git Bash. Manual setup:
```bash
# Set environment variable
set CLAUDE_CODE_GIT_BASH_PATH="C:\Program Files\Git\bin\bash.exe"
```

#### Permission Issues
```bash
# Run with permission bypass
python run_claude.py "your prompt" --dangerously-skip-permissions
```

### Debug Mode
Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Log Files
- **Claude outputs**: `claude_output_YYYYMMDD_HHMMSS.txt`
- **Browser automation**: `logs/browser_automation_*.log`
- **Network analysis**: `logs/network_*.log`
- **Screenshots**: `screenshots/` directory

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Anthropic** for Claude AI integration
- **Selenium** community for web automation tools
- **Chrome DevTools** team for debugging capabilities
- **Python** community for excellent libraries

---

**Note**: This project is designed for defensive security and analysis purposes. Always ensure compliance with applicable laws and terms of service when using web automation tools.

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the troubleshooting section above
- Review log files for detailed error information

---

*Last updated: January 16, 2025*