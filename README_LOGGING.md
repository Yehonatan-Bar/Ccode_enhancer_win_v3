# Comprehensive Logging System

A production-ready logging system with dual-tag architecture for Python applications. This system provides structured logging with feature and module tagging, enabling powerful filtering and analysis capabilities.

## Features

- **Dual-Tag Architecture**: Each log entry has both a feature tag (user-facing functionality) and module tag (internal code structure)
- **Multiple Storage Backends**: Memory, file, and archived file storage with automatic rotation
- **Automatic Log Archiving**: Automatically archives existing logs to timestamped folders on each new session
- **Configurable Filtering**: Enable/disable logging by feature, module, or log level
- **Security-First**: Automatic sanitization of sensitive parameters
- **Comprehensive Analysis**: Built-in log analyzer with feature and module grouping
- **Context Tracking**: Automatic context propagation (user ID, session ID, request ID)
- **Multiple Formatters**: JSON and human-readable formatters
- **Production Ready**: Log rotation, archiving, and performance optimizations
- **Fallback Support**: Graceful fallback to standard Python logging when structured logging is unavailable

## Quick Start

### 1. Basic Setup

```python
from structured_logging import setup_logging, logger, FEATURE_TAGS, MODULE_TAGS

# Initialize the logging system
setup_logging(
    use_console=True,     # Console output
    use_file=True,        # File storage (creates timestamped subdirectories)
    use_memory=True,      # Memory storage for analysis
    log_directory="./logs"
)

# Basic logging
logger.info(
    FEATURE_TAGS.BROWSER_AUTOMATION,
    MODULE_TAGS.BROWSER_MANAGER,
    'launch_browser',
    'Browser launched successfully',
    {'browser_type': 'chrome', 'window_size': '1920x1080'}
)
```

### 1.1 Manual Configuration with Auto-Archiving

For applications that need logs directly in the logs folder with automatic archiving:

```python
import os
import shutil
from datetime import datetime
from structured_logging import logger, FEATURE_TAGS, MODULE_TAGS, config_manager
from structured_logging.storage.file_storage import FileLogStorage
from structured_logging.formatters import ConsoleFormatter

# Load configuration
config_manager.config_file = "logging.json"
config_manager.reload_config()

# Archive existing app.log if it exists
log_dir = "./logs"
app_log_path = os.path.join(log_dir, "app.log")

if os.path.exists(app_log_path):
    # Create timestamped folder for archive
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archive_dir = os.path.join(log_dir, f"archive_{timestamp}")
    os.makedirs(archive_dir, exist_ok=True)
    
    # Move existing app.log to archive
    shutil.move(app_log_path, os.path.join(archive_dir, "app.log"))
    
    # Also move stats and rotated files
    stats_path = os.path.join(log_dir, ".stats.json")
    if os.path.exists(stats_path):
        shutil.move(stats_path, os.path.join(archive_dir, ".stats.json"))
    
    # Move any rotated log files
    for i in range(1, 10):
        for ext in ["", ".gz"]:
            rotated_file = os.path.join(log_dir, f"app.log.{i}{ext}")
            if os.path.exists(rotated_file):
                shutil.move(rotated_file, os.path.join(archive_dir, f"app.log.{i}{ext}"))

# Create standard file storage (NOT archived)
file_storage = FileLogStorage(
    directory="./logs",
    filename="app.log",
    max_file_size=10 * 1024 * 1024,  # 10MB
    max_files=5,
    compress_rotated=True
)

# Create console formatter
console_formatter = ConsoleFormatter()

# Add storage and formatter to logger
logger.add_storage(file_storage)
logger.add_formatter(console_formatter)

# Now you can log
logger.info(
    FEATURE_TAGS.PERFORMANCE,
    MODULE_TAGS.SERVICES,
    'app_start',
    'Application started successfully',
    {'version': '1.0.0'}
)
```

This creates a flat log structure:
```
logs/
├── app.log                    # Current session logs
├── .stats.json               # Current statistics
├── archive_2025-07-17_10-59-18/  # Previous session 1
│   ├── app.log
│   └── .stats.json
└── archive_2025-07-17_10-58-57/  # Previous session 2
    ├── app.log
    └── .stats.json
```

### 2. Configuration

Create a `logging.json` file to control what gets logged:

```python
from structured_logging import create_sample_config

# Creates logging.json with sample configuration
create_sample_config()
```

Example configuration:
```json
{
  "enabled": true,
  "logLevel": "INFO",
  "features": {
    "BROWSER_AUTOMATION": true,
    "ELEMENT_INTERACTION": true,
    "VISION_PROCESSING": true,
    "DEBUG": false
  },
  "modules": {
    "BROWSER_MANAGER": true,
    "ELEMENT_PROCESSORS": true,
    "VISION_PROCESSORS": true,
    "TESTS": false
  }
}
```

### 3. Using Context

```python
from structured_logging import logger, LogContext

# Set context for user session
context = LogContext(
    user_id="user123",
    session_id="session456",
    request_id="req789"
)
logger.set_context(context)

# All subsequent logs will include this context
logger.info(
    FEATURE_TAGS.AUTH,
    MODULE_TAGS.SERVICES,
    'authenticate_user',
    'User authentication successful'
)
```

## Available Tags

### Feature Tags (User-Facing Functionality)
- `BROWSER_AUTOMATION` - Browser control and automation
- `ELEMENT_INTERACTION` - UI element interactions
- `SCREENSHOT_CAPTURE` - Screenshot operations
- `VISION_PROCESSING` - Image and vision processing
- `NETWORK_MONITORING` - Network request monitoring
- `PAGE_ANALYSIS` - Web page analysis
- `AUTH` - Authentication and authorization
- `FILE_OPERATIONS` - File system operations
- `PERFORMANCE` - Performance monitoring
- `ERROR_HANDLING` - Error handling
- And many more...

### Module Tags (Code Structure)
- `BROWSER_MANAGER` - Browser management modules
- `ELEMENT_PROCESSORS` - Element processing modules
- `VISION_PROCESSORS` - Vision processing modules
- `NETWORK_ANALYZERS` - Network analysis modules
- `SERVICES` - Service layer modules
- `CONTROLLERS` - Controller modules
- `UTILS` - Utility modules
- `HANDLERS` - Event handlers
- `STORAGE` - Storage modules
- And many more...

## Log Analysis

```python
from structured_logging import LogAnalyzer, MemoryLogStorage

# Get memory storage for analysis
memory_storage = MemoryLogStorage()
analyzer = LogAnalyzer(memory_storage)

# Overall statistics
stats = analyzer.get_statistics()
print(f"Total logs: {stats['total_logs']}")
print(f"Error rate: {stats['error_rate']:.2%}")

# Group by feature
feature_analysis = analyzer.group_by_feature()
for feature, data in feature_analysis.items():
    print(f"{feature}: {data['total_logs']} logs, {data['error_rate']:.2%} errors")

# Group by module
module_analysis = analyzer.group_by_module()
for module, data in module_analysis.items():
    print(f"{module}: {data['total_logs']} logs, {data['error_rate']:.2%} errors")

# Find recent errors
errors = analyzer.find_errors(limit=10)
for error in errors:
    print(f"{error.timestamp}: {error.feature_tag}:{error.module_tag} - {error.message}")
```

## Security Features

The logging system automatically sanitizes sensitive parameters:

```python
logger.info(
    FEATURE_TAGS.AUTH,
    MODULE_TAGS.SERVICES,
    'user_login',
    'Login attempt',
    {
        'username': 'john.doe',
        'password': 'secret123',  # Automatically redacted as [REDACTED]
        'api_key': 'key-abc123',  # Automatically redacted as [REDACTED]
        'user_agent': 'Chrome/91.0'  # Not sensitive, logged normally
    }
)
```

Sensitive parameter names include:
- password, pwd, pass, secret, token, key
- api_key, apikey, access_token, refresh_token
- private_key, public_key, cert, certificate
- And many more...

## Storage Backends

### Memory Storage
```python
from structured_logging import MemoryLogStorage

memory_storage = MemoryLogStorage(max_entries=10000)
logger.add_storage(memory_storage)
```

### File Storage with Rotation
```python
from structured_logging import FileLogStorage

file_storage = FileLogStorage(
    directory="./logs",
    filename="app.log",
    max_file_size=10 * 1024 * 1024,  # 10MB
    max_files=5,  # Keep 5 rotated files
    compress_rotated=True
)
logger.add_storage(file_storage)
```

### Archived File Storage

The `ArchivedFileLogStorage` automatically creates timestamped subdirectories for each session:

```python
from structured_logging import ArchivedFileLogStorage

archived_storage = ArchivedFileLogStorage(
    base_directory="./logs",
    max_file_size=50 * 1024 * 1024,  # 50MB
    max_files=10
)
logger.add_storage(archived_storage)

# Query archived logs
archives = archived_storage.get_archive_directories()
archived_logs = archived_storage.query_archived_logs(archives[0]['name'])
```

**Note**: This creates logs in timestamped subdirectories:
- `logs/2025-07-17_10-52-22/app.log`
- `logs/2025-07-17_10-53-28/app.log`

If you prefer logs directly in the `logs/` folder with archiving, use the manual configuration approach shown in section 1.1.

## Formatters

### JSON Formatter
```python
from structured_logging import JsonFormatter

json_formatter = JsonFormatter(indent=2)
logger.add_formatter(json_formatter)
```

### Pretty Formatter
```python
# Note: ConsoleFormatter and FileFormatter are in the formatters module
from structured_logging.formatters import ConsoleFormatter, FileFormatter

# For console output (with colors)
console_formatter = ConsoleFormatter()
logger.add_formatter(console_formatter)

# For file output (without colors)
file_formatter = FileFormatter()
logger.add_formatter(file_formatter)
```

**Important**: The `ConsoleFormatter` and `FileFormatter` are located in the `structured_logging.formatters` module, not directly in `structured_logging`. Use the correct import:

```python
# Correct imports
from structured_logging import logger, FEATURE_TAGS, MODULE_TAGS
from structured_logging.formatters import ConsoleFormatter, FileFormatter

# Incorrect imports (will cause ImportError)
# from structured_logging import ConsoleFormatter  # Wrong!
```

## Pre-configured Loggers

For convenience, use pre-configured loggers for common use cases:

```python
from structured_logging import browser_logger, element_logger, vision_logger, network_logger

# Browser automation
browser_logger.info('open_page', 'Navigating to page', {'url': 'https://example.com'})

# Element interaction
element_logger.debug('find_element', 'Searching for element', {'selector': '#submit-btn'})

# Vision processing
vision_logger.info('process_screenshot', 'Screenshot processed', {'resolution': '1920x1080'})

# Network monitoring
network_logger.warn('monitor_requests', 'Slow request detected', {'response_time': 8.5})
```

## Integration with Existing Code

Replace existing logging:

```python
# Before
print(f"Processing user data: {user_data}")
console.log("Failed to save:", error)

# After
from structured_logging import logger, FEATURE_TAGS, MODULE_TAGS

logger.info(
    FEATURE_TAGS.USER_MANAGEMENT,
    MODULE_TAGS.SERVICES,
    'process_user_data',
    'Processing user data',
    {'user_data': user_data}
)

logger.error(
    FEATURE_TAGS.DATABASE,
    MODULE_TAGS.REPOSITORIES,
    'save_data',
    'Failed to save data',
    error
)
```

### Fallback Logger Adapter

When structured logging is not available, use this adapter pattern:

```python
import logging

# Fallback when structured_logging is not available
try:
    from structured_logging import logger, FEATURE_TAGS, MODULE_TAGS
    STRUCTURED_LOGGING_AVAILABLE = True
except ImportError:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    base_logger = logging.getLogger(__name__)
    STRUCTURED_LOGGING_AVAILABLE = False
    
    # Create dummy tags
    class FEATURE_TAGS:
        PERFORMANCE = "PERFORMANCE"
        USER_MANAGEMENT = "USER_MANAGEMENT"
        ERROR_HANDLING = "ERROR_HANDLING"
    
    class MODULE_TAGS:
        SERVICES = "SERVICES"
        COMPONENTS = "COMPONENTS"
        CONTROLLERS = "CONTROLLERS"
    
    # Create adapter that converts structured calls to standard logging
    class LoggerAdapter:
        def __init__(self, logger):
            self.logger = logger
        
        def info(self, feature_tag, module_tag, function_name, message, parameters=None):
            log_msg = f"[{feature_tag}:{module_tag}] {function_name} - {message}"
            if parameters:
                log_msg += f" | {parameters}"
            self.logger.info(log_msg)
        
        def debug(self, feature_tag, module_tag, function_name, message, parameters=None):
            log_msg = f"[{feature_tag}:{module_tag}] {function_name} - {message}"
            if parameters:
                log_msg += f" | {parameters}"
            self.logger.debug(log_msg)
        
        def warning(self, feature_tag, module_tag, function_name, message, parameters=None):
            log_msg = f"[{feature_tag}:{module_tag}] {function_name} - {message}"
            if parameters:
                log_msg += f" | {parameters}"
            self.logger.warning(log_msg)
        
        def error(self, feature_tag, module_tag, function_name, message, exception=None, parameters=None):
            log_msg = f"[{feature_tag}:{module_tag}] {function_name} - {message}"
            if parameters:
                log_msg += f" | {parameters}"
            if exception:
                log_msg += f" | Exception: {exception}"
            self.logger.error(log_msg)
    
    logger = LoggerAdapter(base_logger)

# Now use the same API regardless of availability
logger.info(
    FEATURE_TAGS.PERFORMANCE,
    MODULE_TAGS.SERVICES,
    'process_data',
    'Processing data',
    {'size': 1024}
)
```

## Examples

Run the examples to see the system in action:

```python
from structured_logging.examples import run_all_examples

run_all_examples()
```

This will:
1. Create a sample configuration file
2. Demonstrate all logging features
3. Show analysis capabilities
4. Display security features

## Best Practices

1. **Use Appropriate Log Levels**
   - DEBUG: Development debugging
   - INFO: Normal application flow
   - WARN: Recoverable issues
   - ERROR: Errors needing attention
   - FATAL: Critical errors

2. **Choose Correct Tags**
   - Feature tags: What functionality is being used
   - Module tags: Where in the code the log originates

3. **Include Relevant Parameters**
   - Help with debugging and analysis
   - System will automatically sanitize sensitive data

4. **Set Context for Sessions**
   - Use user_id, session_id, request_id for tracing
   - Clear context when sessions end

5. **Configure for Environment**
   - Development: Enable DEBUG, all features
   - Production: Enable WARN+, critical features only

## Performance Considerations

- Logging is disabled by default for security
- Only enabled features/modules are processed
- File storage uses efficient JSON format
- Memory storage has configurable limits
- Automatic log rotation prevents disk fill-up

## Architecture

```
structured_logging/
├── __init__.py           # Main exports and setup
├── types.py              # Core types and interfaces
├── constants.py          # Feature and module tags
├── config.py             # Configuration management
├── logger.py             # Main Logger class
├── analyzer.py           # Log analysis tools
├── examples.py           # Usage examples
├── storage/              # Storage backends
│   ├── memory_storage.py
│   ├── file_storage.py
│   └── archived_file_storage.py
└── formatters/           # Output formatters
    ├── json_formatter.py
    └── pretty_formatter.py
```

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'structured_logging.formatters.console_formatter'**
   - Solution: Use `from structured_logging.formatters import ConsoleFormatter` instead

2. **Logs creating timestamped subdirectories instead of app.log in logs folder**
   - Solution: Use manual configuration with `FileLogStorage` instead of `setup_logging(use_file=True)`
   - The default `setup_logging` uses `ArchivedFileLogStorage` which creates timestamped directories

3. **TypeError: not all arguments converted during string formatting**
   - This occurs when structured logging falls back to standard Python logging
   - Ensure structured_logging is properly installed and accessible
   - Use the LoggerAdapter pattern for graceful fallback

4. **No logs appearing**
   - Check if logging is enabled in `logging.json`
   - Verify the feature and module tags are enabled in configuration
   - Ensure the log directory exists and has write permissions

5. **Unicode encoding errors in console output**
   - This can occur on Windows with special characters
   - Replace Unicode symbols (✓, ✗) with ASCII alternatives ([OK], [FAIL])

### Log File Locations

Default behavior with `setup_logging(use_file=True)`:
```
logs/
└── 2025-07-17_10-52-22/     # Timestamped directory
    ├── app.log               # Log file
    └── .stats.json           # Statistics
```

With manual archiving configuration:
```
logs/
├── app.log                   # Current session (direct in logs/)
├── .stats.json              # Current statistics
└── archive_2025-07-17_10-59-18/  # Archived previous session
    ├── app.log
    └── .stats.json
```

## License

This logging system is designed for production use and can be freely integrated into any Python project.