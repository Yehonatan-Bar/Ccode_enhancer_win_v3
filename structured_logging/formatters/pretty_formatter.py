from datetime import datetime
from typing import Dict, Any, Optional
from ..types import LogEntry, LogFormatter, LogLevel


class PrettyFormatter:
    """Human-readable formatter for log entries"""
    
    def __init__(self, 
                 show_timestamp: bool = True,
                 show_level: bool = True,
                 show_tags: bool = True,
                 show_function: bool = True,
                 show_parameters: bool = True,
                 show_context: bool = True,
                 show_exception: bool = True,
                 timestamp_format: str = "%Y-%m-%d %H:%M:%S",
                 use_colors: bool = True):
        self.show_timestamp = show_timestamp
        self.show_level = show_level
        self.show_tags = show_tags
        self.show_function = show_function
        self.show_parameters = show_parameters
        self.show_context = show_context
        self.show_exception = show_exception
        self.timestamp_format = timestamp_format
        self.use_colors = use_colors
        
        # Color codes for different log levels
        self.colors = {
            LogLevel.DEBUG: '\033[36m',    # Cyan
            LogLevel.INFO: '\033[32m',     # Green
            LogLevel.WARN: '\033[33m',     # Yellow
            LogLevel.ERROR: '\033[31m',    # Red
            LogLevel.FATAL: '\033[35m',    # Magenta
        }
        self.reset_color = '\033[0m'
    
    def _colorize(self, text: str, level: LogLevel) -> str:
        """Apply color to text based on log level"""
        if not self.use_colors:
            return text
        
        color = self.colors.get(level, '')
        return f"{color}{text}{self.reset_color}"
    
    def format(self, entry: LogEntry) -> str:
        """Format a log entry in human-readable format"""
        
        parts = []
        
        # Timestamp
        if self.show_timestamp:
            timestamp_str = entry.timestamp.strftime(self.timestamp_format)
            parts.append(f"[{timestamp_str}]")
        
        # Level
        if self.show_level:
            level_str = entry.level.value.ljust(5)
            level_str = self._colorize(level_str, entry.level)
            parts.append(f"{level_str}")
        
        # Tags
        if self.show_tags:
            tags_str = f"[{entry.feature_tag}:{entry.module_tag}]"
            parts.append(tags_str)
        
        # Function name
        if self.show_function:
            parts.append(f"{entry.function_name}()")
        
        # Message
        message = self._colorize(entry.message, entry.level)
        parts.append(f"- {message}")
        
        # Create main log line
        main_line = " ".join(parts)
        
        # Additional information
        additional_lines = []
        
        # Parameters
        if self.show_parameters and entry.parameters:
            params_str = self._format_parameters(entry.parameters)
            additional_lines.append(f"  Parameters: {params_str}")
        
        # Context
        if self.show_context and entry.context:
            context_str = self._format_context(entry.context)
            additional_lines.append(f"  Context: {context_str}")
        
        # Exception
        if self.show_exception and entry.exception:
            exception_str = self._format_exception(entry.exception)
            additional_lines.append(f"  Exception: {exception_str}")
        
        # Combine all lines
        if additional_lines:
            return main_line + "\n" + "\n".join(additional_lines)
        else:
            return main_line
    
    def _format_parameters(self, parameters: Dict[str, Any]) -> str:
        """Format parameters dictionary"""
        if not parameters:
            return "{}"
        
        # Format parameters in a readable way
        formatted_params = []
        for key, value in parameters.items():
            if isinstance(value, str):
                formatted_params.append(f"{key}='{value}'")
            else:
                formatted_params.append(f"{key}={value}")
        
        return "{" + ", ".join(formatted_params) + "}"
    
    def _format_context(self, context) -> str:
        """Format context information"""
        context_parts = []
        
        if context.user_id:
            context_parts.append(f"user_id={context.user_id}")
        
        if context.session_id:
            context_parts.append(f"session_id={context.session_id}")
        
        if context.request_id:
            context_parts.append(f"request_id={context.request_id}")
        
        if context.additional_context:
            for key, value in context.additional_context.items():
                context_parts.append(f"{key}={value}")
        
        return "{" + ", ".join(context_parts) + "}"
    
    def _format_exception(self, exception: Exception) -> str:
        """Format exception information"""
        return f"{exception.__class__.__name__}: {str(exception)}"
    
    def format_compact(self, entry: LogEntry) -> str:
        """Format a log entry in compact format"""
        formatter = PrettyFormatter(
            show_timestamp=True,
            show_level=True,
            show_tags=False,
            show_function=False,
            show_parameters=False,
            show_context=False,
            show_exception=False,
            use_colors=self.use_colors
        )
        return formatter.format(entry)
    
    def format_detailed(self, entry: LogEntry) -> str:
        """Format a log entry with all details"""
        formatter = PrettyFormatter(
            show_timestamp=True,
            show_level=True,
            show_tags=True,
            show_function=True,
            show_parameters=True,
            show_context=True,
            show_exception=True,
            use_colors=self.use_colors
        )
        return formatter.format(entry)


class ConsoleFormatter(PrettyFormatter):
    """Formatter optimized for console output"""
    
    def __init__(self):
        super().__init__(
            show_timestamp=True,
            show_level=True,
            show_tags=True,
            show_function=True,
            show_parameters=True,
            show_context=False,  # Skip context for console to reduce clutter
            show_exception=True,
            use_colors=True
        )


class FileFormatter(PrettyFormatter):
    """Formatter optimized for file output"""
    
    def __init__(self):
        super().__init__(
            show_timestamp=True,
            show_level=True,
            show_tags=True,
            show_function=True,
            show_parameters=True,
            show_context=True,
            show_exception=True,
            use_colors=False  # No colors for file output
        )