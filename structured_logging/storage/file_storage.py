import os
import json
import gzip
from typing import List, Optional, Dict, Any
from datetime import datetime
from collections import defaultdict
from ..types import LogEntry, LogLevel, LogStorage
from ..formatters.json_formatter import JsonFormatter


class FileLogStorage:
    def __init__(self, 
                 directory: str = "./logs",
                 filename: str = "app.log",
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 max_files: int = 5,
                 compress_rotated: bool = True):
        self.directory = directory
        self.filename = filename
        self.max_file_size = max_file_size
        self.max_files = max_files
        self.compress_rotated = compress_rotated
        self.formatter = JsonFormatter()
        
        # Ensure directory exists
        os.makedirs(directory, exist_ok=True)
        
        self._current_file_path = os.path.join(directory, filename)
        self._statistics = self._load_statistics()
    
    def _get_file_size(self) -> int:
        """Get current log file size"""
        try:
            return os.path.getsize(self._current_file_path)
        except OSError:
            return 0
    
    def _should_rotate(self) -> bool:
        """Check if log rotation is needed"""
        return self._get_file_size() >= self.max_file_size
    
    def _rotate_logs(self) -> None:
        """Rotate log files"""
        if not os.path.exists(self._current_file_path):
            return
        
        # Remove oldest log file
        oldest_file = os.path.join(self.directory, f"{self.filename}.{self.max_files}")
        if self.compress_rotated:
            oldest_file += ".gz"
        
        if os.path.exists(oldest_file):
            os.remove(oldest_file)
        
        # Rotate existing files
        for i in range(self.max_files, 0, -1):
            current_file = os.path.join(self.directory, f"{self.filename}.{i}")
            next_file = os.path.join(self.directory, f"{self.filename}.{i + 1}")
            
            if self.compress_rotated:
                current_file += ".gz"
                next_file += ".gz"
            
            if os.path.exists(current_file):
                os.rename(current_file, next_file)
        
        # Move current file to .1
        rotated_file = os.path.join(self.directory, f"{self.filename}.1")
        
        if self.compress_rotated:
            # Compress the rotated file
            with open(self._current_file_path, 'rb') as f_in:
                with gzip.open(f"{rotated_file}.gz", 'wb') as f_out:
                    f_out.writelines(f_in)
            os.remove(self._current_file_path)
        else:
            os.rename(self._current_file_path, rotated_file)
    
    def store(self, entry: LogEntry) -> None:
        """Store a log entry"""
        # Check if rotation is needed
        if self._should_rotate():
            self._rotate_logs()
        
        # Format and write entry
        formatted_entry = self.formatter.format(entry)
        
        try:
            with open(self._current_file_path, 'a', encoding='utf-8') as f:
                f.write(formatted_entry + '\n')
            
            # Update statistics
            self._update_statistics(entry)
            
        except Exception as e:
            print(f"Failed to write log entry to file: {e}")
    
    def _update_statistics(self, entry: LogEntry) -> None:
        """Update statistics for new entry"""
        self._statistics['total_logs'] += 1
        self._statistics['by_level'][entry.level.value] += 1
        self._statistics['by_feature'][entry.feature_tag] += 1
        self._statistics['by_module'][entry.module_tag] += 1
        self._save_statistics()
    
    def _load_statistics(self) -> Dict[str, Any]:
        """Load statistics from file"""
        stats_file = os.path.join(self.directory, ".stats.json")
        try:
            if os.path.exists(stats_file):
                with open(stats_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        
        return {
            'total_logs': 0,
            'by_level': defaultdict(int),
            'by_feature': defaultdict(int),
            'by_module': defaultdict(int)
        }
    
    def _save_statistics(self) -> None:
        """Save statistics to file"""
        stats_file = os.path.join(self.directory, ".stats.json")
        try:
            with open(stats_file, 'w') as f:
                json.dump(self._statistics, f, indent=2)
        except Exception as e:
            print(f"Failed to save statistics: {e}")
    
    def query(self, 
              level: Optional[LogLevel] = None,
              feature_tag: Optional[str] = None,
              module_tag: Optional[str] = None,
              user_id: Optional[str] = None,
              start_time: Optional[datetime] = None,
              end_time: Optional[datetime] = None,
              limit: Optional[int] = None,
              offset: Optional[int] = None) -> List[LogEntry]:
        """Query log entries from all log files"""
        
        entries = []
        
        # Get all log files (current + rotated)
        log_files = [self._current_file_path]
        
        for i in range(1, self.max_files + 1):
            rotated_file = os.path.join(self.directory, f"{self.filename}.{i}")
            
            if self.compress_rotated:
                rotated_file += ".gz"
                if os.path.exists(rotated_file):
                    log_files.append(rotated_file)
            else:
                if os.path.exists(rotated_file):
                    log_files.append(rotated_file)
        
        # Read entries from all files
        for log_file in log_files:
            entries.extend(self._read_entries_from_file(log_file))
        
        # Apply filters
        filtered_entries = self._apply_filters(
            entries, level, feature_tag, module_tag, user_id, start_time, end_time
        )
        
        # Sort by timestamp (newest first)
        filtered_entries.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply offset and limit
        if offset:
            filtered_entries = filtered_entries[offset:]
        
        if limit:
            filtered_entries = filtered_entries[:limit]
        
        return filtered_entries
    
    def _read_entries_from_file(self, file_path: str) -> List[LogEntry]:
        """Read log entries from a single file"""
        entries = []
        
        try:
            if file_path.endswith('.gz'):
                opener = gzip.open
                mode = 'rt'
            else:
                opener = open
                mode = 'r'
            
            with opener(file_path, mode, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        entry_data = json.loads(line)
                        entry = self._dict_to_log_entry(entry_data)
                        if entry:
                            entries.append(entry)
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            print(f"Failed to read log file {file_path}: {e}")
        
        return entries
    
    def _dict_to_log_entry(self, data: Dict[str, Any]) -> Optional[LogEntry]:
        """Convert dictionary to LogEntry"""
        try:
            from ..types import LogContext
            
            # Parse context
            context = None
            if data.get('context'):
                context_data = data['context']
                context = LogContext(
                    user_id=context_data.get('user_id'),
                    session_id=context_data.get('session_id'),
                    request_id=context_data.get('request_id'),
                    additional_context=context_data.get('additional_context')
                )
            
            # Parse exception
            exception = None
            if data.get('exception'):
                exception = Exception(data['exception'])
            
            return LogEntry(
                timestamp=datetime.fromisoformat(data['timestamp']),
                level=LogLevel(data['level']),
                feature_tag=data['feature_tag'],
                module_tag=data['module_tag'],
                function_name=data['function_name'],
                message=data['message'],
                parameters=data.get('parameters'),
                context=context,
                exception=exception
            )
        except Exception:
            return None
    
    def _apply_filters(self, 
                      entries: List[LogEntry],
                      level: Optional[LogLevel] = None,
                      feature_tag: Optional[str] = None,
                      module_tag: Optional[str] = None,
                      user_id: Optional[str] = None,
                      start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None) -> List[LogEntry]:
        """Apply filters to log entries"""
        
        filtered_entries = []
        
        for entry in entries:
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
        
        return filtered_entries
    
    def clear(self) -> None:
        """Clear all log files"""
        # Remove current log file
        if os.path.exists(self._current_file_path):
            os.remove(self._current_file_path)
        
        # Remove rotated files
        for i in range(1, self.max_files + 1):
            rotated_file = os.path.join(self.directory, f"{self.filename}.{i}")
            
            if self.compress_rotated:
                rotated_file += ".gz"
            
            if os.path.exists(rotated_file):
                os.remove(rotated_file)
        
        # Reset statistics
        self._statistics = {
            'total_logs': 0,
            'by_level': defaultdict(int),
            'by_feature': defaultdict(int),
            'by_module': defaultdict(int)
        }
        self._save_statistics()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics"""
        return {
            'total_logs': self._statistics['total_logs'],
            'by_level': dict(self._statistics['by_level']),
            'by_feature': dict(self._statistics['by_feature']),
            'by_module': dict(self._statistics['by_module']),
            'storage_type': 'file',
            'directory': self.directory,
            'current_file_size': self._get_file_size(),
            'max_file_size': self.max_file_size,
            'max_files': self.max_files,
            'compress_rotated': self.compress_rotated
        }