from typing import List, Optional, Dict, Any
from datetime import datetime
from collections import defaultdict
from ..types import LogEntry, LogLevel, LogStorage


class MemoryLogStorage:
    def __init__(self, max_entries: int = 10000):
        self.max_entries = max_entries
        self._entries: List[LogEntry] = []
        self._statistics = {
            'total_logs': 0,
            'by_level': defaultdict(int),
            'by_feature': defaultdict(int),
            'by_module': defaultdict(int)
        }
    
    def store(self, entry: LogEntry) -> None:
        """Store a log entry"""
        self._entries.append(entry)
        
        # Update statistics
        self._statistics['total_logs'] += 1
        self._statistics['by_level'][entry.level.value] += 1
        self._statistics['by_feature'][entry.feature_tag] += 1
        self._statistics['by_module'][entry.module_tag] += 1
        
        # Maintain max entries limit
        if len(self._entries) > self.max_entries:
            removed = self._entries.pop(0)
            # Update statistics for removed entry
            self._statistics['total_logs'] -= 1
            self._statistics['by_level'][removed.level.value] -= 1
            self._statistics['by_feature'][removed.feature_tag] -= 1
            self._statistics['by_module'][removed.module_tag] -= 1
    
    def query(self, 
              level: Optional[LogLevel] = None,
              feature_tag: Optional[str] = None,
              module_tag: Optional[str] = None,
              user_id: Optional[str] = None,
              start_time: Optional[datetime] = None,
              end_time: Optional[datetime] = None,
              limit: Optional[int] = None,
              offset: Optional[int] = None) -> List[LogEntry]:
        """Query log entries with filters"""
        
        filtered_entries = []
        
        for entry in self._entries:
            # Apply filters
            if level and entry.level != level:
                continue
            
            if feature_tag and entry.feature_tag != feature_tag:
                continue
            
            if module_tag and entry.module_tag != module_tag:
                continue
            
            if user_id and (not entry.context or entry.context.user_id != user_id):
                continue
            
            if start_time and entry.timestamp < start_time:
                continue
            
            if end_time and entry.timestamp > end_time:
                continue
            
            filtered_entries.append(entry)
        
        # Sort by timestamp (newest first)
        filtered_entries.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply offset and limit
        if offset:
            filtered_entries = filtered_entries[offset:]
        
        if limit:
            filtered_entries = filtered_entries[:limit]
        
        return filtered_entries
    
    def clear(self) -> None:
        """Clear all log entries"""
        self._entries.clear()
        self._statistics = {
            'total_logs': 0,
            'by_level': defaultdict(int),
            'by_feature': defaultdict(int),
            'by_module': defaultdict(int)
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics"""
        return {
            'total_logs': self._statistics['total_logs'],
            'by_level': dict(self._statistics['by_level']),
            'by_feature': dict(self._statistics['by_feature']),
            'by_module': dict(self._statistics['by_module']),
            'storage_type': 'memory',
            'max_entries': self.max_entries,
            'current_entries': len(self._entries)
        }
    
    def get_entries_count(self) -> int:
        """Get current number of entries"""
        return len(self._entries)
    
    def get_memory_usage_estimate(self) -> int:
        """Get estimated memory usage in bytes"""
        # Rough estimate based on average entry size
        avg_entry_size = 500  # bytes
        return len(self._entries) * avg_entry_size