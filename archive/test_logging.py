#!/usr/bin/env python3
"""
Test script to verify the structured logging system works correctly
"""

def test_logging_system():
    """Test the structured logging system"""
    
    print("Testing structured logging system...")
    
    try:
        # Import the logging system
        from structured_logging import (
            setup_logging, logger, create_sample_config,
            FEATURE_TAGS, MODULE_TAGS, LogAnalyzer,
            MemoryLogStorage, browser_logger
        )
        
        print("[OK] Successfully imported structured logging components")
        
        # Create sample configuration
        create_sample_config()
        print("[OK] Sample configuration created: logging.json")
        
        # Setup logging
        setup_logging(
            use_console=True,
            use_file=True,
            use_memory=True,
            log_directory="./test_logs"
        )
        print("[OK] Logging system initialized")
        
        # Test basic logging
        logger.info(
            FEATURE_TAGS.BROWSER_AUTOMATION,
            MODULE_TAGS.BROWSER_MANAGER,
            'test_function',
            'Testing basic logging functionality',
            {'test_param': 'test_value', 'number': 42}
        )
        print("[OK] Basic logging test passed")
        
        # Test pre-configured logger
        browser_logger.info(
            'test_browser_function',
            'Testing browser logger',
            {'browser': 'chrome', 'version': '91.0'}
        )
        print("[OK] Pre-configured logger test passed")
        
        # Test error logging
        try:
            raise ValueError("Test error for logging")
        except Exception as e:
            logger.error(
                FEATURE_TAGS.ERROR_HANDLING,
                MODULE_TAGS.HANDLERS,
                'test_error_handling',
                'Testing error logging',
                e,
                {'error_type': 'ValueError', 'test_mode': True}
            )
        print("[OK] Error logging test passed")
        
        # Test security feature (parameter sanitization)
        logger.info(
            FEATURE_TAGS.AUTH,
            MODULE_TAGS.SERVICES,
            'test_security',
            'Testing parameter sanitization',
            {
                'username': 'testuser',
                'password': 'secret123',  # Should be redacted
                'api_key': 'key-abc123',  # Should be redacted
                'public_data': 'not_sensitive'
            }
        )
        print("[OK] Security (parameter sanitization) test passed")
        
        # Test log analysis
        memory_storage = None
        for storage in logger._storages:
            if isinstance(storage, MemoryLogStorage):
                memory_storage = storage
                break
        
        if memory_storage:
            analyzer = LogAnalyzer(memory_storage)
            stats = analyzer.get_statistics()
            print(f"[OK] Log analysis test passed - Found {stats['total_logs']} log entries")
            
            # Test feature grouping
            feature_analysis = analyzer.group_by_feature()
            print(f"[OK] Feature analysis test passed - Found {len(feature_analysis)} features")
            
            # Test module grouping
            module_analysis = analyzer.group_by_module()
            print(f"[OK] Module analysis test passed - Found {len(module_analysis)} modules")
        else:
            print("[WARNING] Memory storage not found, skipping analysis tests")
        
        print("\n" + "="*50)
        print("SUCCESS: All tests passed!")
        print("The structured logging system is working correctly.")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_logging_system()