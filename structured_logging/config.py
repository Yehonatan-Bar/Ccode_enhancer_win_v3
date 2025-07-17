import json
import os
from typing import Dict, Any, Optional
from .types import LoggingConfig, LogLevel
from .constants import FEATURE_TAGS, MODULE_TAGS


class LoggingConfigManager:
    def __init__(self, config_file: str = "logging.json"):
        self.config_file = config_file
        self._config = self._get_default_config()
        self._load_config()
    
    def _get_default_config(self) -> LoggingConfig:
        """Get default configuration with all features/modules disabled for security"""
        default_features = {
            FEATURE_TAGS.AUTH: False,
            FEATURE_TAGS.PROJECT_MANAGEMENT: False,
            FEATURE_TAGS.USER_MANAGEMENT: False,
            FEATURE_TAGS.SECURITY: False,
            FEATURE_TAGS.ERROR_HANDLING: True,  # Always allow error logging
            FEATURE_TAGS.BROWSER_AUTOMATION: False,
            FEATURE_TAGS.ELEMENT_INTERACTION: False,
            FEATURE_TAGS.SCREENSHOT_CAPTURE: False,
            FEATURE_TAGS.NETWORK_MONITORING: False,
            FEATURE_TAGS.PAGE_ANALYSIS: False,
            FEATURE_TAGS.VISION_PROCESSING: False,
            FEATURE_TAGS.IMAGE_COMPRESSION: False,
            FEATURE_TAGS.ELEMENT_DETECTION: False,
            FEATURE_TAGS.FILE_OPERATIONS: False,
            FEATURE_TAGS.CONFIGURATION: False,
            FEATURE_TAGS.MONITORING: False,
            FEATURE_TAGS.DEBUG: False,
            FEATURE_TAGS.TESTING: False,
            FEATURE_TAGS.PERFORMANCE: False,
            FEATURE_TAGS.SYSTEM_INTEGRATION: False,
            FEATURE_TAGS.HARDWARE_DETECTION: False,
            FEATURE_TAGS.LOGGING: True,  # Always allow logging system logs
        }
        
        default_modules = {
            MODULE_TAGS.SERVICES: False,
            MODULE_TAGS.CONTROLLERS: False,
            MODULE_TAGS.HANDLERS: True,  # Always allow handler logs
            MODULE_TAGS.UTILS: False,
            MODULE_TAGS.BROWSER_MANAGER: False,
            MODULE_TAGS.ELEMENT_PROCESSORS: False,
            MODULE_TAGS.NETWORK_ANALYZERS: False,
            MODULE_TAGS.VISION_PROCESSORS: False,
            MODULE_TAGS.STORAGE: False,
            MODULE_TAGS.FORMATTERS: False,
            MODULE_TAGS.VALIDATORS: False,
            MODULE_TAGS.ANALYZERS: False,
            MODULE_TAGS.MIDDLEWARE: False,
            MODULE_TAGS.REPOSITORIES: False,
            MODULE_TAGS.MODELS: False,
            MODULE_TAGS.COMPONENTS: False,
            MODULE_TAGS.TESTS: False,
            MODULE_TAGS.TOOLS: False,
            MODULE_TAGS.SCRIPTS: False,
            MODULE_TAGS.CONFIGS: False,
        }
        
        return LoggingConfig(
            enabled=False,  # Disabled by default for security
            log_level=LogLevel.INFO,
            features=default_features,
            modules=default_modules
        )
    
    def _load_config(self) -> None:
        """Load configuration from JSON file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Update configuration with loaded data
                self._config.enabled = config_data.get('enabled', False)
                self._config.log_level = LogLevel(config_data.get('logLevel', 'INFO'))
                
                # Update features with loaded data
                if 'features' in config_data:
                    self._config.features.update(config_data['features'])
                
                # Update modules with loaded data
                if 'modules' in config_data:
                    self._config.modules.update(config_data['modules'])
                    
        except Exception as e:
            print(f"Warning: Failed to load logging config from {self.config_file}: {e}")
            print("Using default configuration")
    
    def is_enabled(self) -> bool:
        """Check if logging is globally enabled"""
        return self._config.enabled
    
    def is_level_enabled(self, level: LogLevel) -> bool:
        """Check if the given log level is enabled"""
        level_order = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.WARN: 2,
            LogLevel.ERROR: 3,
            LogLevel.FATAL: 4
        }
        return level_order[level] >= level_order[self._config.log_level]
    
    def is_feature_enabled(self, feature_tag: str) -> bool:
        """Check if the given feature tag is enabled"""
        return self._config.features.get(feature_tag, False)
    
    def is_module_enabled(self, module_tag: str) -> bool:
        """Check if the given module tag is enabled"""
        return self._config.modules.get(module_tag, False)
    
    def should_log(self, level: LogLevel, feature_tag: str, module_tag: str) -> bool:
        """Check if a log entry should be processed"""
        return (
            self.is_enabled() and
            self.is_level_enabled(level) and
            self.is_feature_enabled(feature_tag) and
            self.is_module_enabled(module_tag)
        )
    
    def get_config(self) -> LoggingConfig:
        """Get current configuration"""
        return self._config
    
    def reload_config(self) -> None:
        """Reload configuration from file"""
        self._load_config()
    
    def create_sample_config(self) -> None:
        """Create a sample configuration file"""
        sample_config = {
            "enabled": True,
            "logLevel": "INFO",
            "features": {
                "AUTH": True,
                "PROJECT_MANAGEMENT": True,
                "BROWSER_AUTOMATION": True,
                "ELEMENT_INTERACTION": True,
                "SCREENSHOT_CAPTURE": True,
                "NETWORK_MONITORING": True,
                "PAGE_ANALYSIS": True,
                "VISION_PROCESSING": True,
                "IMAGE_COMPRESSION": True,
                "ELEMENT_DETECTION": True,
                "FILE_OPERATIONS": True,
                "CONFIGURATION": True,
                "MONITORING": True,
                "DEBUG": False,
                "TESTING": False,
                "PERFORMANCE": False,
                "SYSTEM_INTEGRATION": True,
                "HARDWARE_DETECTION": True,
                "LOGGING": True,
                "USER_MANAGEMENT": True,
                "SECURITY": True,
                "ERROR_HANDLING": True
            },
            "modules": {
                "SERVICES": True,
                "CONTROLLERS": True,
                "HANDLERS": True,
                "UTILS": True,
                "BROWSER_MANAGER": True,
                "ELEMENT_PROCESSORS": True,
                "NETWORK_ANALYZERS": True,
                "VISION_PROCESSORS": True,
                "STORAGE": True,
                "FORMATTERS": True,
                "VALIDATORS": True,
                "ANALYZERS": True,
                "MIDDLEWARE": True,
                "REPOSITORIES": True,
                "MODELS": True,
                "COMPONENTS": True,
                "TESTS": False,
                "TOOLS": True,
                "SCRIPTS": True,
                "CONFIGS": True
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(sample_config, f, indent=2)
        
        print(f"Sample configuration created at {self.config_file}")
        print("Restart the application to apply changes")


# Global configuration manager instance
config_manager = LoggingConfigManager()