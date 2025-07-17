import os
import shutil
from datetime import datetime
from typing import List, Optional, Dict, Any
from .file_storage import FileLogStorage
from ..types import LogEntry, LogLevel


class ArchivedFileLogStorage(FileLogStorage):
    """Enhanced file storage with automatic archiving of previous sessions"""
    
    def __init__(self, 
                 base_directory: str = "./logs",
                 filename: str = "app.log",
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 max_files: int = 5,
                 compress_rotated: bool = True,
                 archive_previous_sessions: bool = True):
        
        self.base_directory = base_directory
        self.archive_previous_sessions = archive_previous_sessions
        
        # Create timestamped directory for current session
        self.current_session_dir = self._create_session_directory()
        
        # Archive existing logs if enabled
        if self.archive_previous_sessions:
            self._archive_existing_logs()
        
        # Initialize with current session directory
        super().__init__(
            directory=self.current_session_dir,
            filename=filename,
            max_file_size=max_file_size,
            max_files=max_files,
            compress_rotated=compress_rotated
        )
    
    def _create_session_directory(self) -> str:
        """Create a timestamped directory for the current session"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        session_dir = os.path.join(self.base_directory, timestamp)
        os.makedirs(session_dir, exist_ok=True)
        return session_dir
    
    def _archive_existing_logs(self) -> None:
        """Archive existing log files from previous sessions"""
        if not os.path.exists(self.base_directory):
            return
        
        # Look for existing log files in the base directory
        log_files = []
        for item in os.listdir(self.base_directory):
            item_path = os.path.join(self.base_directory, item)
            
            # Skip if it's already a timestamped directory
            if os.path.isdir(item_path) and self._is_timestamped_directory(item):
                continue
            
            # Check if it's a log file
            if os.path.isfile(item_path) and (
                item.endswith('.log') or 
                item.endswith('.log.gz') or 
                item.startswith('.stats.json')
            ):
                log_files.append(item_path)
        
        # If there are existing log files, create an archive directory
        if log_files:
            # Find the latest modification time to determine archive timestamp
            latest_mtime = max(os.path.getmtime(f) for f in log_files)
            archive_timestamp = datetime.fromtimestamp(latest_mtime).strftime("%Y-%m-%d_%H-%M-%S")
            archive_dir = os.path.join(self.base_directory, f"archived_{archive_timestamp}")
            
            # Create archive directory
            os.makedirs(archive_dir, exist_ok=True)
            
            # Move existing files to archive
            for file_path in log_files:
                filename = os.path.basename(file_path)
                archive_path = os.path.join(archive_dir, filename)
                try:
                    shutil.move(file_path, archive_path)
                except Exception as e:
                    print(f"Failed to archive {file_path}: {e}")
    
    def _is_timestamped_directory(self, dirname: str) -> bool:
        """Check if directory name follows timestamp format"""
        try:
            # Try to parse as timestamp format
            datetime.strptime(dirname.split('_')[0], "%Y-%m-%d")
            return True
        except (ValueError, IndexError):
            return dirname.startswith("archived_")
    
    def get_archive_directories(self) -> List[Dict[str, Any]]:
        """Get list of archived log directories"""
        archives = []
        
        if not os.path.exists(self.base_directory):
            return archives
        
        for item in os.listdir(self.base_directory):
            item_path = os.path.join(self.base_directory, item)
            
            if os.path.isdir(item_path) and item_path != self.current_session_dir:
                try:
                    # Get directory stats
                    stat = os.stat(item_path)
                    
                    # Count log files in directory
                    log_files = []
                    for file in os.listdir(item_path):
                        if file.endswith('.log') or file.endswith('.log.gz'):
                            log_files.append(file)
                    
                    archives.append({
                        'name': item,
                        'path': item_path,
                        'created': datetime.fromtimestamp(stat.st_ctime),
                        'modified': datetime.fromtimestamp(stat.st_mtime),
                        'log_files': log_files,
                        'file_count': len(log_files)
                    })
                except Exception as e:
                    print(f"Failed to read archive directory {item_path}: {e}")
        
        # Sort by creation time (newest first)
        archives.sort(key=lambda x: x['created'], reverse=True)
        return archives
    
    def query_archived_logs(self, 
                           archive_name: str,
                           level: Optional[LogLevel] = None,
                           feature_tag: Optional[str] = None,
                           module_tag: Optional[str] = None,
                           user_id: Optional[str] = None,
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None,
                           limit: Optional[int] = None,
                           offset: Optional[int] = None) -> List[LogEntry]:
        """Query logs from a specific archive directory"""
        
        archive_path = os.path.join(self.base_directory, archive_name)
        
        if not os.path.exists(archive_path) or not os.path.isdir(archive_path):
            return []
        
        # Temporarily create a FileLogStorage for the archive directory
        archive_storage = FileLogStorage(
            directory=archive_path,
            filename=self.filename,
            max_file_size=self.max_file_size,
            max_files=self.max_files,
            compress_rotated=self.compress_rotated
        )
        
        return archive_storage.query(
            level, feature_tag, module_tag, user_id, start_time, end_time, limit, offset
        )
    
    def query(self, 
              level: Optional[LogLevel] = None,
              feature_tag: Optional[str] = None,
              module_tag: Optional[str] = None,
              user_id: Optional[str] = None,
              start_time: Optional[datetime] = None,
              end_time: Optional[datetime] = None,
              limit: Optional[int] = None,
              offset: Optional[int] = None,
              include_archived: bool = False) -> List[LogEntry]:
        """Query logs with optional archived session inclusion"""
        
        # Get logs from current session
        current_logs = super().query(
            level, feature_tag, module_tag, user_id, start_time, end_time, limit, offset
        )
        
        # If not including archived logs, return current logs
        if not include_archived:
            return current_logs
        
        # Get logs from all archived sessions
        archived_logs = []
        for archive in self.get_archive_directories():
            try:
                archive_logs = self.query_archived_logs(
                    archive['name'], level, feature_tag, module_tag, user_id, start_time, end_time
                )
                archived_logs.extend(archive_logs)
            except Exception as e:
                print(f"Failed to query archived logs from {archive['name']}: {e}")
        
        # Combine and sort all logs
        all_logs = current_logs + archived_logs
        all_logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply offset and limit to combined results
        if offset:
            all_logs = all_logs[offset:]
        
        if limit:
            all_logs = all_logs[:limit]
        
        return all_logs
    
    def export_logs(self, 
                   archive_name: Optional[str] = None,
                   format: str = "json",
                   output_file: Optional[str] = None) -> str:
        """Export logs to file"""
        
        if archive_name:
            # Export from specific archive
            entries = self.query_archived_logs(archive_name)
            if not output_file:
                output_file = f"logs_export_{archive_name}.{format}"
        else:
            # Export from current session
            entries = super().query()
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"logs_export_{timestamp}.{format}"
        
        # Export based on format
        if format.lower() == "json":
            self._export_json(entries, output_file)
        elif format.lower() == "csv":
            self._export_csv(entries, output_file)
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        return output_file
    
    def _export_json(self, entries: List[LogEntry], output_file: str) -> None:
        """Export entries to JSON format"""
        import json
        
        json_data = []
        for entry in entries:
            json_data.append({
                'timestamp': entry.timestamp.isoformat(),
                'level': entry.level.value,
                'feature_tag': entry.feature_tag,
                'module_tag': entry.module_tag,
                'function_name': entry.function_name,
                'message': entry.message,
                'parameters': entry.parameters,
                'context': {
                    'user_id': entry.context.user_id if entry.context else None,
                    'session_id': entry.context.session_id if entry.context else None,
                    'request_id': entry.context.request_id if entry.context else None,
                    'additional_context': entry.context.additional_context if entry.context else None
                } if entry.context else None,
                'exception': str(entry.exception) if entry.exception else None
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    def _export_csv(self, entries: List[LogEntry], output_file: str) -> None:
        """Export entries to CSV format"""
        import csv
        
        fieldnames = [
            'timestamp', 'level', 'feature_tag', 'module_tag', 'function_name',
            'message', 'parameters', 'user_id', 'session_id', 'request_id', 'exception'
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for entry in entries:
                writer.writerow({
                    'timestamp': entry.timestamp.isoformat(),
                    'level': entry.level.value,
                    'feature_tag': entry.feature_tag,
                    'module_tag': entry.module_tag,
                    'function_name': entry.function_name,
                    'message': entry.message,
                    'parameters': str(entry.parameters) if entry.parameters else '',
                    'user_id': entry.context.user_id if entry.context else '',
                    'session_id': entry.context.session_id if entry.context else '',
                    'request_id': entry.context.request_id if entry.context else '',
                    'exception': str(entry.exception) if entry.exception else ''
                })
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get enhanced statistics including archive information"""
        base_stats = super().get_statistics()
        
        # Add archive information
        archives = self.get_archive_directories()
        base_stats.update({
            'storage_type': 'archived_file',
            'current_session_dir': self.current_session_dir,
            'archive_count': len(archives),
            'archives': [
                {
                    'name': archive['name'],
                    'file_count': archive['file_count'],
                    'created': archive['created'].isoformat(),
                    'modified': archive['modified'].isoformat()
                }
                for archive in archives
            ]
        })
        
        return base_stats