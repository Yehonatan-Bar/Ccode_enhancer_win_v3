import json
from datetime import datetime
from typing import Dict, Any, Optional
from ..types import LogEntry, LogFormatter


class JsonFormatter:
    """JSON formatter for log entries"""
    
    def __init__(self, indent: Optional[int] = None, ensure_ascii: bool = False):
        self.indent = indent
        self.ensure_ascii = ensure_ascii
    
    def format(self, entry: LogEntry) -> str:
        """Format a log entry as JSON"""
        
        # Convert LogEntry to dictionary
        entry_dict = {
            'timestamp': entry.timestamp.isoformat(),
            'level': entry.level.value,
            'feature_tag': entry.feature_tag,
            'module_tag': entry.module_tag,
            'function_name': entry.function_name,
            'message': entry.message
        }
        
        # Add parameters if present
        if entry.parameters:
            entry_dict['parameters'] = entry.parameters
        
        # Add context if present
        if entry.context:
            context_dict = {}
            if entry.context.user_id:
                context_dict['user_id'] = entry.context.user_id
            if entry.context.session_id:
                context_dict['session_id'] = entry.context.session_id
            if entry.context.request_id:
                context_dict['request_id'] = entry.context.request_id
            if entry.context.additional_context:
                context_dict['additional_context'] = entry.context.additional_context
            
            if context_dict:
                entry_dict['context'] = context_dict
        
        # Add exception if present
        if entry.exception:
            entry_dict['exception'] = {
                'type': entry.exception.__class__.__name__,
                'message': str(entry.exception),
                'args': entry.exception.args
            }
        
        # Convert to JSON
        return json.dumps(entry_dict, indent=self.indent, ensure_ascii=self.ensure_ascii)
    
    def format_compact(self, entry: LogEntry) -> str:
        """Format a log entry as compact JSON (single line)"""
        formatter = JsonFormatter(indent=None, ensure_ascii=self.ensure_ascii)
        return formatter.format(entry)
    
    def format_pretty(self, entry: LogEntry) -> str:
        """Format a log entry as pretty JSON (indented)"""
        formatter = JsonFormatter(indent=2, ensure_ascii=self.ensure_ascii)
        return formatter.format(entry)