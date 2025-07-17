# Comprehensive Logging System

A production-ready logging system with dual-tag architecture for Python applications. This system provides structured logging with feature and module tagging, enabling powerful filtering and analysis capabilities.

## Features

- **Dual-Tag Architecture**: Each log entry has both a feature tag (user-facing functionality) and module tag (internal code structure)
- **Multiple Storage Backends**: Memory, file, and archived file storage with automatic rotation
- **Configurable Filtering**: Enable/disable logging by feature, module, or log level
- **Security-First**: Automatic sanitization of sensitive parameters
- **Comprehensive Analysis**: Built-in log analyzer with feature and module grouping
- **Context Tracking**: Automatic context propagation (user ID, session ID, request ID)
- **Multiple Formatters**: JSON and human-readable formatters
- **Production Ready**: Log rotation, archiving, and performance optimizations

## Quick Start

### 1. Basic Setup

```python
from structured_logging import setup_logging, logger, FEATURE_TAGS, MODULE_TAGS

# Initialize the logging system
setup_logging(
    use_console=True,     # Console output
    use_file=True,        # File storage
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

## Formatters

### JSON Formatter
```python
from structured_logging import JsonFormatter

json_formatter = JsonFormatter(indent=2)
logger.add_formatter(json_formatter)
```

### Pretty Formatter
```python
from structured_logging import ConsoleFormatter, FileFormatter

# For console output (with colors)
console_formatter = ConsoleFormatter()
logger.add_formatter(console_formatter)

# For file output (without colors)
file_formatter = FileFormatter()
logger.add_formatter(file_formatter)
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

## License

This logging system is designed for production use and can be freely integrated into any Python project.