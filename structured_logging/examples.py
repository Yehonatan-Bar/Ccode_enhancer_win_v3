"""
Example usage of the logging system with dual-tag architecture

This module demonstrates how to use the logging system in various scenarios
with proper feature and module tagging.
"""

from . import (
    logger, setup_logging, create_sample_config, LogAnalyzer,
    FEATURE_TAGS, MODULE_TAGS, COMMON_TAG_COMBINATIONS,
    MemoryLogStorage, ArchivedFileLogStorage,
    browser_logger, element_logger, vision_logger, network_logger
)
from .types import LogContext


def example_basic_usage():
    """Basic logging usage examples"""
    
    print("=== Basic Logging Examples ===")
    
    # Setup logging system
    setup_logging(use_console=True, use_file=True, use_memory=True)
    
    # Basic info logging
    logger.info(
        FEATURE_TAGS.BROWSER_AUTOMATION,
        MODULE_TAGS.BROWSER_MANAGER,
        'launch_browser',
        'Browser launched successfully',
        {'browser_type': 'chrome', 'window_size': '1920x1080'}
    )
    
    # Error logging with exception
    try:
        raise ValueError("Sample error for demonstration")
    except Exception as e:
        logger.error(
            FEATURE_TAGS.ELEMENT_INTERACTION,
            MODULE_TAGS.ELEMENT_PROCESSORS,
            'click_element',
            'Failed to click element',
            e,
            {'element_id': 'submit-button', 'attempt': 3}
        )
    
    # Debug logging
    logger.debug(
        FEATURE_TAGS.VISION_PROCESSING,
        MODULE_TAGS.VISION_PROCESSORS,
        'detect_elements',
        'Processing screenshot for element detection',
        {'image_size': '1920x1080', 'detection_threshold': 0.8}
    )
    
    # Warning logging
    logger.warn(
        FEATURE_TAGS.PERFORMANCE,
        MODULE_TAGS.ANALYZERS,
        'analyze_performance',
        'Performance degradation detected',
        {'response_time': 5.2, 'threshold': 3.0}
    )


def example_context_usage():
    """Examples of using logging context"""
    
    print("=== Context Logging Examples ===")
    
    # Set context for a user session
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
    
    # Update context with additional information
    logger.update_context(page_url="https://example.com", action="login")
    
    logger.info(
        FEATURE_TAGS.PAGE_ANALYSIS,
        MODULE_TAGS.ANALYZERS,
        'analyze_page',
        'Page analysis completed',
        {'elements_found': 15, 'load_time': 2.3}
    )
    
    # Clear context when session ends
    logger.clear_context()


def example_feature_module_loggers():
    """Examples using pre-configured feature/module loggers"""
    
    print("=== Feature-Module Logger Examples ===")
    
    # Browser automation logging
    browser_logger.info(
        'open_page',
        'Navigating to target page',
        {'url': 'https://example.com', 'timeout': 30}
    )
    
    # Element interaction logging
    element_logger.debug(
        'find_element',
        'Searching for clickable element',
        {'selector': '#submit-btn', 'method': 'css_selector'}
    )
    
    # Vision processing logging
    vision_logger.info(
        'process_screenshot',
        'Screenshot captured and processed',
        {'resolution': '1920x1080', 'file_size': '245KB'}
    )
    
    # Network monitoring logging
    network_logger.warn(
        'monitor_requests',
        'Slow network request detected',
        {'url': '/api/data', 'response_time': 8.5, 'status': 200}
    )


def example_common_tag_combinations():
    """Examples using predefined tag combinations"""
    
    print("=== Common Tag Combinations Examples ===")
    
    # Use predefined combinations for convenience
    for combo_name, (feature_tag, module_tag) in COMMON_TAG_COMBINATIONS.items():
        logger.info(
            feature_tag,
            module_tag,
            f'example_{combo_name}',
            f'Example log for {combo_name} combination',
            {'combination': combo_name}
        )


def example_log_analysis():
    """Examples of log analysis functionality"""
    
    print("=== Log Analysis Examples ===")
    
    # Get memory storage for analysis
    memory_storage = None
    for storage in logger._storages:
        if isinstance(storage, MemoryLogStorage):
            memory_storage = storage
            break
    
    if not memory_storage:
        print("No memory storage found for analysis")
        return
    
    analyzer = LogAnalyzer(memory_storage)
    
    # Get overall statistics
    stats = analyzer.get_statistics()
    print(f"Total logs: {stats['total_logs']}")
    print(f"Error rate: {stats['error_rate']:.2%}")
    print(f"Most active features: {stats['most_active_features'][:3]}")
    print(f"Most active modules: {stats['most_active_modules'][:3]}")
    
    # Analyze by feature
    feature_analysis = analyzer.group_by_feature()
    print("\n--- Feature Analysis ---")
    for feature, analysis in list(feature_analysis.items())[:3]:
        print(f"{feature}: {analysis['total_logs']} logs, {analysis['error_rate']:.2%} error rate")
    
    # Analyze by module
    module_analysis = analyzer.group_by_module()
    print("\n--- Module Analysis ---")
    for module, analysis in list(module_analysis.items())[:3]:
        print(f"{module}: {analysis['total_logs']} logs, {analysis['error_rate']:.2%} error rate")
    
    # Find recent errors
    errors = analyzer.find_errors(limit=5)
    print(f"\n--- Recent Errors ({len(errors)}) ---")
    for error in errors:
        print(f"{error.timestamp}: {error.feature_tag}:{error.module_tag} - {error.message}")


def example_storage_configuration():
    """Examples of different storage configurations"""
    
    print("=== Storage Configuration Examples ===")
    
    # Memory storage only (for development)
    memory_storage = MemoryLogStorage(max_entries=1000)
    
    # File storage with archiving (for production)
    file_storage = ArchivedFileLogStorage(
        base_directory="./production_logs",
        max_file_size=50 * 1024 * 1024,  # 50MB
        max_files=10
    )
    
    # Create a new logger instance for this example
    from .logger import Logger
    example_logger = Logger()
    example_logger.add_storage(memory_storage)
    example_logger.add_storage(file_storage)
    
    # Log some example entries
    example_logger.info(
        FEATURE_TAGS.CONFIGURATION,
        MODULE_TAGS.CONFIGS,
        'setup_storage',
        'Storage configuration completed',
        {'memory_limit': 1000, 'file_limit': '50MB'}
    )
    
    print("Storage configuration example completed")


def example_security_features():
    """Examples demonstrating security features"""
    
    print("=== Security Features Examples ===")
    
    # Sensitive parameters will be automatically redacted
    logger.info(
        FEATURE_TAGS.AUTH,
        MODULE_TAGS.SERVICES,
        'user_login',
        'User login attempt',
        {
            'username': 'john.doe',
            'password': 'secret123',  # Will be redacted
            'api_key': 'key-abc123',  # Will be redacted
            'session_token': 'token-xyz',  # Will be redacted
            'user_agent': 'Chrome/91.0',  # Will not be redacted
            'ip_address': '192.168.1.1'  # Will not be redacted
        }
    )
    
    # Nested sensitive data will also be redacted
    logger.info(
        FEATURE_TAGS.SYSTEM_INTEGRATION,
        MODULE_TAGS.SERVICES,
        'api_call',
        'Making API call',
        {
            'url': 'https://api.example.com/data',
            'headers': {
                'Authorization': 'Bearer secret-token',  # Will be redacted
                'Content-Type': 'application/json'  # Will not be redacted
            },
            'credentials': {
                'username': 'admin',
                'password': 'admin123'  # Will be redacted
            }
        }
    )


def run_all_examples():
    """Run all example functions"""
    
    print("Starting Logging System Examples")
    print("=" * 50)
    
    # Create sample configuration file
    create_sample_config()
    print("Sample configuration file created: logging.json")
    print("Edit this file to customize logging behavior")
    print()
    
    # Run examples
    example_basic_usage()
    print()
    
    example_context_usage()
    print()
    
    example_feature_module_loggers()
    print()
    
    example_common_tag_combinations()
    print()
    
    example_security_features()
    print()
    
    example_storage_configuration()
    print()
    
    example_log_analysis()
    print()
    
    print("=" * 50)
    print("All examples completed!")
    print()
    print("Next steps:")
    print("1. Edit logging.json to enable desired features and modules")
    print("2. Integrate logging into your existing codebase")
    print("3. Use the analyzer to monitor and analyze your logs")
    print("4. Set up proper storage backends for production use")


if __name__ == "__main__":
    run_all_examples()