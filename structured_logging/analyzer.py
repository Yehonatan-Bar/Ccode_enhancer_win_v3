from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from .types import LogEntry, LogLevel, LogStorage
from .constants import FEATURE_TAGS, MODULE_TAGS


class LogAnalyzer:
    """Comprehensive log analysis tool with feature and module sorting"""
    
    def __init__(self, storage: LogStorage):
        self.storage = storage
    
    def get_statistics(self, 
                      start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Get comprehensive log statistics"""
        
        # Query all logs within time range
        logs = self.storage.query(start_time=start_time, end_time=end_time)
        
        if not logs:
            return {
                'total_logs': 0,
                'time_range': {
                    'start': start_time.isoformat() if start_time else None,
                    'end': end_time.isoformat() if end_time else None
                },
                'by_level': {},
                'by_feature': {},
                'by_module': {},
                'by_hour': {},
                'error_rate': 0.0,
                'most_active_features': [],
                'most_active_modules': [],
                'error_distribution': {}
            }
        
        # Basic counts
        total_logs = len(logs)
        level_counts = Counter(log.level.value for log in logs)
        feature_counts = Counter(log.feature_tag for log in logs)
        module_counts = Counter(log.module_tag for log in logs)
        
        # Time-based analysis
        hour_counts = defaultdict(int)
        for log in logs:
            hour_key = log.timestamp.strftime('%Y-%m-%d %H:00')
            hour_counts[hour_key] += 1
        
        # Error analysis
        error_logs = [log for log in logs if log.level in [LogLevel.ERROR, LogLevel.FATAL]]
        error_rate = len(error_logs) / total_logs if total_logs > 0 else 0.0
        
        # Most active features and modules
        most_active_features = feature_counts.most_common(10)
        most_active_modules = module_counts.most_common(10)
        
        # Error distribution by feature and module
        error_by_feature = Counter(log.feature_tag for log in error_logs)
        error_by_module = Counter(log.module_tag for log in error_logs)
        
        return {
            'total_logs': total_logs,
            'time_range': {
                'start': start_time.isoformat() if start_time else logs[-1].timestamp.isoformat(),
                'end': end_time.isoformat() if end_time else logs[0].timestamp.isoformat(),
                'duration_hours': (logs[0].timestamp - logs[-1].timestamp).total_seconds() / 3600
            },
            'by_level': dict(level_counts),
            'by_feature': dict(feature_counts),
            'by_module': dict(module_counts),
            'by_hour': dict(hour_counts),
            'error_rate': error_rate,
            'most_active_features': most_active_features,
            'most_active_modules': most_active_modules,
            'error_distribution': {
                'by_feature': dict(error_by_feature),
                'by_module': dict(error_by_module)
            }
        }
    
    def group_by_feature(self, 
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None) -> Dict[str, Dict[str, Any]]:
        """Group logs by feature tag with detailed analysis"""
        
        logs = self.storage.query(start_time=start_time, end_time=end_time)
        feature_groups = defaultdict(list)
        
        # Group logs by feature
        for log in logs:
            feature_groups[log.feature_tag].append(log)
        
        # Analyze each feature group
        feature_analysis = {}
        for feature, feature_logs in feature_groups.items():
            # Basic stats
            total_logs = len(feature_logs)
            level_counts = Counter(log.level.value for log in feature_logs)
            module_counts = Counter(log.module_tag for log in feature_logs)
            function_counts = Counter(log.function_name for log in feature_logs)
            
            # Time analysis
            timestamps = [log.timestamp for log in feature_logs]
            time_span = max(timestamps) - min(timestamps) if timestamps else timedelta(0)
            
            # Error analysis
            error_logs = [log for log in feature_logs if log.level in [LogLevel.ERROR, LogLevel.FATAL]]
            error_rate = len(error_logs) / total_logs if total_logs > 0 else 0.0
            
            # Most common functions and modules
            top_functions = function_counts.most_common(5)
            top_modules = module_counts.most_common(5)
            
            feature_analysis[feature] = {
                'total_logs': total_logs,
                'by_level': dict(level_counts),
                'by_module': dict(module_counts),
                'top_functions': top_functions,
                'top_modules': top_modules,
                'error_rate': error_rate,
                'error_count': len(error_logs),
                'time_span': time_span.total_seconds() / 3600,  # hours
                'first_log': min(timestamps).isoformat() if timestamps else None,
                'last_log': max(timestamps).isoformat() if timestamps else None,
                'logs_per_hour': total_logs / max(1, time_span.total_seconds() / 3600)
            }
        
        return feature_analysis
    
    def group_by_module(self, 
                       start_time: Optional[datetime] = None,
                       end_time: Optional[datetime] = None) -> Dict[str, Dict[str, Any]]:
        """Group logs by module tag with detailed analysis"""
        
        logs = self.storage.query(start_time=start_time, end_time=end_time)
        module_groups = defaultdict(list)
        
        # Group logs by module
        for log in logs:
            module_groups[log.module_tag].append(log)
        
        # Analyze each module group
        module_analysis = {}
        for module, module_logs in module_groups.items():
            # Basic stats
            total_logs = len(module_logs)
            level_counts = Counter(log.level.value for log in module_logs)
            feature_counts = Counter(log.feature_tag for log in module_logs)
            function_counts = Counter(log.function_name for log in module_logs)
            
            # Time analysis
            timestamps = [log.timestamp for log in module_logs]
            time_span = max(timestamps) - min(timestamps) if timestamps else timedelta(0)
            
            # Error analysis
            error_logs = [log for log in module_logs if log.level in [LogLevel.ERROR, LogLevel.FATAL]]
            error_rate = len(error_logs) / total_logs if total_logs > 0 else 0.0
            
            # Most common functions and features
            top_functions = function_counts.most_common(5)
            top_features = feature_counts.most_common(5)
            
            module_analysis[module] = {
                'total_logs': total_logs,
                'by_level': dict(level_counts),
                'by_feature': dict(feature_counts),
                'top_functions': top_functions,
                'top_features': top_features,
                'error_rate': error_rate,
                'error_count': len(error_logs),
                'time_span': time_span.total_seconds() / 3600,  # hours
                'first_log': min(timestamps).isoformat() if timestamps else None,
                'last_log': max(timestamps).isoformat() if timestamps else None,
                'logs_per_hour': total_logs / max(1, time_span.total_seconds() / 3600)
            }
        
        return module_analysis
    
    def find_errors(self, 
                   limit: Optional[int] = None,
                   feature_tag: Optional[str] = None,
                   module_tag: Optional[str] = None) -> List[LogEntry]:
        """Find error and fatal logs with optional filtering"""
        
        error_logs = []
        
        # Query ERROR logs
        error_logs.extend(
            self.storage.query(
                level=LogLevel.ERROR,
                feature_tag=feature_tag,
                module_tag=module_tag,
                limit=limit
            )
        )
        
        # Query FATAL logs
        fatal_logs = self.storage.query(
            level=LogLevel.FATAL,
            feature_tag=feature_tag,
            module_tag=module_tag,
            limit=limit
        )
        error_logs.extend(fatal_logs)
        
        # Sort by timestamp (newest first)
        error_logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply limit if specified
        if limit:
            error_logs = error_logs[:limit]
        
        return error_logs
    
    def get_user_activity(self, 
                         user_id: str,
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Analyze activity for a specific user"""
        
        logs = self.storage.query(
            user_id=user_id,
            start_time=start_time,
            end_time=end_time
        )
        
        if not logs:
            return {
                'user_id': user_id,
                'total_logs': 0,
                'activity_summary': {}
            }
        
        # Basic analysis
        total_logs = len(logs)
        level_counts = Counter(log.level.value for log in logs)
        feature_counts = Counter(log.feature_tag for log in logs)
        module_counts = Counter(log.module_tag for log in logs)
        function_counts = Counter(log.function_name for log in logs)
        
        # Time analysis
        timestamps = [log.timestamp for log in logs]
        session_duration = max(timestamps) - min(timestamps) if timestamps else timedelta(0)
        
        # Activity patterns (by hour of day)
        hour_activity = defaultdict(int)
        for log in logs:
            hour_activity[log.timestamp.hour] += 1
        
        return {
            'user_id': user_id,
            'total_logs': total_logs,
            'session_duration_hours': session_duration.total_seconds() / 3600,
            'first_activity': min(timestamps).isoformat() if timestamps else None,
            'last_activity': max(timestamps).isoformat() if timestamps else None,
            'by_level': dict(level_counts),
            'by_feature': dict(feature_counts),
            'by_module': dict(module_counts),
            'top_functions': function_counts.most_common(10),
            'hourly_activity': dict(hour_activity),
            'most_active_hour': max(hour_activity.items(), key=lambda x: x[1])[0] if hour_activity else None
        }
    
    def detect_anomalies(self, 
                        time_window_hours: int = 1,
                        threshold_multiplier: float = 3.0) -> List[Dict[str, Any]]:
        """Detect anomalies in logging patterns"""
        
        # Get logs from last 24 hours for baseline
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        logs = self.storage.query(start_time=start_time, end_time=end_time)
        
        if not logs:
            return []
        
        # Group logs by time windows
        window_counts = defaultdict(int)
        for log in logs:
            window_key = int(log.timestamp.timestamp() // (time_window_hours * 3600))
            window_counts[window_key] += 1
        
        # Calculate statistics
        counts = list(window_counts.values())
        if not counts:
            return []
        
        avg_count = sum(counts) / len(counts)
        std_dev = (sum((x - avg_count) ** 2 for x in counts) / len(counts)) ** 0.5
        threshold = avg_count + (threshold_multiplier * std_dev)
        
        # Find anomalies
        anomalies = []
        for window_key, count in window_counts.items():
            if count > threshold:
                window_start = datetime.fromtimestamp(window_key * time_window_hours * 3600)
                window_end = window_start + timedelta(hours=time_window_hours)
                
                # Get logs in this window for details
                window_logs = [
                    log for log in logs 
                    if window_start <= log.timestamp < window_end
                ]
                
                feature_counts = Counter(log.feature_tag for log in window_logs)
                module_counts = Counter(log.module_tag for log in window_logs)
                level_counts = Counter(log.level.value for log in window_logs)
                
                anomalies.append({
                    'window_start': window_start.isoformat(),
                    'window_end': window_end.isoformat(),
                    'log_count': count,
                    'expected_count': avg_count,
                    'severity': (count - avg_count) / std_dev if std_dev > 0 else 0,
                    'top_features': feature_counts.most_common(5),
                    'top_modules': module_counts.most_common(5),
                    'by_level': dict(level_counts)
                })
        
        return sorted(anomalies, key=lambda x: x['severity'], reverse=True)
    
    def generate_report(self, 
                       start_time: Optional[datetime] = None,
                       end_time: Optional[datetime] = None,
                       include_feature_analysis: bool = True,
                       include_module_analysis: bool = True,
                       include_anomalies: bool = True) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'time_range': {
                'start': start_time.isoformat() if start_time else None,
                'end': end_time.isoformat() if end_time else None
            }
        }
        
        # Overall statistics
        report['statistics'] = self.get_statistics(start_time, end_time)
        
        # Feature analysis
        if include_feature_analysis:
            report['feature_analysis'] = self.group_by_feature(start_time, end_time)
        
        # Module analysis
        if include_module_analysis:
            report['module_analysis'] = self.group_by_module(start_time, end_time)
        
        # Recent errors
        report['recent_errors'] = [
            {
                'timestamp': log.timestamp.isoformat(),
                'level': log.level.value,
                'feature_tag': log.feature_tag,
                'module_tag': log.module_tag,
                'function_name': log.function_name,
                'message': log.message,
                'exception': str(log.exception) if log.exception else None
            }
            for log in self.find_errors(limit=20)
        ]
        
        # Anomaly detection
        if include_anomalies:
            report['anomalies'] = self.detect_anomalies()
        
        return report