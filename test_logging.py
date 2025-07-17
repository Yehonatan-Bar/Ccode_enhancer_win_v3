import os
import sys
import shutil
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from structured_logging import logger, FEATURE_TAGS, MODULE_TAGS, config_manager
from structured_logging.storage.file_storage import FileLogStorage
from structured_logging.formatters import ConsoleFormatter

# Load configuration
config_manager.config_file = "logging.json"
config_manager.reload_config()

# Archive existing app.log if it exists
log_dir = "./logs"
app_log_path = os.path.join(log_dir, "app.log")

if os.path.exists(app_log_path):
    # Create timestamped folder for archive
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archive_dir = os.path.join(log_dir, f"archive_{timestamp}")
    os.makedirs(archive_dir, exist_ok=True)
    
    # Move existing app.log to archive
    archive_path = os.path.join(archive_dir, "app.log")
    shutil.move(app_log_path, archive_path)
    print(f"Archived existing app.log to {archive_dir}")
    
    # Also move stats file if exists
    stats_path = os.path.join(log_dir, ".stats.json")
    if os.path.exists(stats_path):
        shutil.move(stats_path, os.path.join(archive_dir, ".stats.json"))

# Ensure logs directory exists
os.makedirs(log_dir, exist_ok=True)

# Create standard file storage (NOT archived)
file_storage = FileLogStorage(
    directory="./logs",
    filename="app.log",
    max_file_size=10 * 1024 * 1024,  # 10MB
    max_files=5,
    compress_rotated=True
)

# Create console formatter
console_formatter = ConsoleFormatter()

# Add storage and formatter to logger
logger.add_storage(file_storage)
logger.add_formatter(console_formatter)

# Test logging
logger.info(
    FEATURE_TAGS.PERFORMANCE,
    MODULE_TAGS.SERVICES,
    'test_logging',
    'Testing logging system',
    {'test': 'successful', 'timestamp': datetime.now().isoformat()}
)

print(f"\nChecking if app.log was created...")
if os.path.exists(app_log_path):
    print(f"[OK] app.log created successfully in {log_dir}")
    print(f"File size: {os.path.getsize(app_log_path)} bytes")
else:
    print(f"[FAIL] app.log not found in {log_dir}")

# List contents of logs directory
print(f"\nContents of {log_dir}:")
for item in os.listdir(log_dir):
    print(f"  - {item}")