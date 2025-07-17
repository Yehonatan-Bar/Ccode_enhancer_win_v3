from enum import Enum
from typing import Dict, Any, Optional, List, Union, Protocol
from datetime import datetime
from dataclasses import dataclass


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"


@dataclass
class LogContext:
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    additional_context: Optional[Dict[str, Any]] = None


@dataclass
class LogEntry:
    timestamp: datetime
    level: LogLevel
    feature_tag: str
    module_tag: str
    function_name: str
    message: str
    parameters: Optional[Dict[str, Any]] = None
    context: Optional[LogContext] = None
    exception: Optional[Exception] = None


@dataclass
class LoggingConfig:
    enabled: bool = False
    log_level: LogLevel = LogLevel.INFO
    features: Dict[str, bool] = None
    modules: Dict[str, bool] = None
    
    def __post_init__(self):
        if self.features is None:
            self.features = {}
        if self.modules is None:
            self.modules = {}


class LogStorage(Protocol):
    def store(self, entry: LogEntry) -> None:
        ...
    
    def query(self, 
              level: Optional[LogLevel] = None,
              feature_tag: Optional[str] = None,
              module_tag: Optional[str] = None,
              user_id: Optional[str] = None,
              start_time: Optional[datetime] = None,
              end_time: Optional[datetime] = None,
              limit: Optional[int] = None,
              offset: Optional[int] = None) -> List[LogEntry]:
        ...
    
    def clear(self) -> None:
        ...
    
    def get_statistics(self) -> Dict[str, Any]:
        ...


class LogFormatter(Protocol):
    def format(self, entry: LogEntry) -> str:
        ...


class FilterResult(Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"