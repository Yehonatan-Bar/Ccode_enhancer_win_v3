import copy
from datetime import datetime
from typing import Dict, Any, Optional, List
from .types import LogLevel, LogEntry, LogContext, LogStorage, LogFormatter
from .config import config_manager
from .constants import SENSITIVE_PARAMETERS


class Logger:
    def __init__(self):
        self._storages: List[LogStorage] = []
        self._formatters: List[LogFormatter] = []
        self._context: Optional[LogContext] = None
    
    def add_storage(self, storage: LogStorage) -> None:
        """Add a storage backend"""
        self._storages.append(storage)
    
    def add_formatter(self, formatter: LogFormatter) -> None:
        """Add a formatter"""
        self._formatters.append(formatter)
    
    def set_context(self, context: LogContext) -> None:
        """Set the current logging context"""
        self._context = context
    
    def update_context(self, **kwargs) -> None:
        """Update the current logging context"""
        if self._context is None:
            self._context = LogContext()
        
        for key, value in kwargs.items():
            if hasattr(self._context, key):
                setattr(self._context, key, value)
            else:
                if self._context.additional_context is None:
                    self._context.additional_context = {}
                self._context.additional_context[key] = value
    
    def clear_context(self) -> None:
        """Clear the current logging context"""
        self._context = None
    
    def _sanitize_parameters(self, parameters: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Sanitize sensitive parameters"""
        if not parameters:
            return parameters
        
        sanitized = copy.deepcopy(parameters)
        
        def _sanitize_recursive(obj: Any) -> Any:
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key.lower() in SENSITIVE_PARAMETERS:
                        obj[key] = '[REDACTED]'
                    else:
                        obj[key] = _sanitize_recursive(value)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    obj[i] = _sanitize_recursive(item)
            return obj
        
        return _sanitize_recursive(sanitized)
    
    def _should_log(self, level: LogLevel, feature_tag: str, module_tag: str) -> bool:
        """Check if this log entry should be processed"""
        return config_manager.should_log(level, feature_tag, module_tag)
    
    def _create_log_entry(self, 
                         level: LogLevel,
                         feature_tag: str,
                         module_tag: str,
                         function_name: str,
                         message: str,
                         parameters: Optional[Dict[str, Any]] = None,
                         exception: Optional[Exception] = None) -> LogEntry:
        """Create a log entry"""
        return LogEntry(
            timestamp=datetime.now(),
            level=level,
            feature_tag=feature_tag,
            module_tag=module_tag,
            function_name=function_name,
            message=message,
            parameters=self._sanitize_parameters(parameters),
            context=copy.deepcopy(self._context) if self._context else None,
            exception=exception
        )
    
    def _log(self, 
            level: LogLevel,
            feature_tag: str,
            module_tag: str,
            function_name: str,
            message: str,
            parameters: Optional[Dict[str, Any]] = None,
            exception: Optional[Exception] = None) -> None:
        """Internal logging method"""
        
        # Check if logging should occur
        if not self._should_log(level, feature_tag, module_tag):
            return
        
        # Create log entry
        entry = self._create_log_entry(
            level, feature_tag, module_tag, function_name, message, parameters, exception
        )
        
        # Store in all storage backends
        for storage in self._storages:
            try:
                storage.store(entry)
            except Exception as e:
                # Prevent logging failures from breaking the application
                print(f"Failed to store log entry: {e}")
        
        # Format and output (if formatters are configured)
        for formatter in self._formatters:
            try:
                formatted = formatter.format(entry)
                print(formatted)
            except Exception as e:
                print(f"Failed to format log entry: {e}")
    
    def debug(self, 
             feature_tag: str,
             module_tag: str,
             function_name: str,
             message: str,
             parameters: Optional[Dict[str, Any]] = None) -> None:
        """Log a debug message"""
        self._log(LogLevel.DEBUG, feature_tag, module_tag, function_name, message, parameters)
    
    def info(self, 
            feature_tag: str,
            module_tag: str,
            function_name: str,
            message: str,
            parameters: Optional[Dict[str, Any]] = None) -> None:
        """Log an info message"""
        self._log(LogLevel.INFO, feature_tag, module_tag, function_name, message, parameters)
    
    def warn(self, 
            feature_tag: str,
            module_tag: str,
            function_name: str,
            message: str,
            parameters: Optional[Dict[str, Any]] = None) -> None:
        """Log a warning message"""
        self._log(LogLevel.WARN, feature_tag, module_tag, function_name, message, parameters)
    
    def error(self, 
             feature_tag: str,
             module_tag: str,
             function_name: str,
             message: str,
             exception: Optional[Exception] = None,
             parameters: Optional[Dict[str, Any]] = None) -> None:
        """Log an error message"""
        self._log(LogLevel.ERROR, feature_tag, module_tag, function_name, message, parameters, exception)
    
    def fatal(self, 
             feature_tag: str,
             module_tag: str,
             function_name: str,
             message: str,
             exception: Optional[Exception] = None,
             parameters: Optional[Dict[str, Any]] = None) -> None:
        """Log a fatal message"""
        self._log(LogLevel.FATAL, feature_tag, module_tag, function_name, message, parameters, exception)
    
    def query_logs(self, 
                  level: Optional[LogLevel] = None,
                  feature_tag: Optional[str] = None,
                  module_tag: Optional[str] = None,
                  user_id: Optional[str] = None,
                  start_time: Optional[datetime] = None,
                  end_time: Optional[datetime] = None,
                  limit: Optional[int] = None,
                  offset: Optional[int] = None) -> List[LogEntry]:
        """Query logs from all storage backends"""
        all_logs = []
        for storage in self._storages:
            try:
                logs = storage.query(level, feature_tag, module_tag, user_id, start_time, end_time, limit, offset)
                all_logs.extend(logs)
            except Exception as e:
                print(f"Failed to query logs from storage: {e}")
        
        # Sort by timestamp and apply limit/offset if specified
        all_logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        if offset:
            all_logs = all_logs[offset:]
        if limit:
            all_logs = all_logs[:limit]
        
        return all_logs
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get logging statistics from all storage backends"""
        stats = {
            'total_logs': 0,
            'by_level': {},
            'by_feature': {},
            'by_module': {},
            'storage_backends': len(self._storages),
            'formatters': len(self._formatters)
        }
        
        for storage in self._storages:
            try:
                storage_stats = storage.get_statistics()
                # Aggregate statistics
                stats['total_logs'] += storage_stats.get('total_logs', 0)
                
                # Merge level statistics
                for level, count in storage_stats.get('by_level', {}).items():
                    stats['by_level'][level] = stats['by_level'].get(level, 0) + count
                
                # Merge feature statistics
                for feature, count in storage_stats.get('by_feature', {}).items():
                    stats['by_feature'][feature] = stats['by_feature'].get(feature, 0) + count
                
                # Merge module statistics
                for module, count in storage_stats.get('by_module', {}).items():
                    stats['by_module'][module] = stats['by_module'].get(module, 0) + count
                    
            except Exception as e:
                print(f"Failed to get statistics from storage: {e}")
        
        return stats
    
    def clear_logs(self) -> None:
        """Clear all logs from storage backends"""
        for storage in self._storages:
            try:
                storage.clear()
            except Exception as e:
                print(f"Failed to clear logs from storage: {e}")


# Global logger instance
logger = Logger()