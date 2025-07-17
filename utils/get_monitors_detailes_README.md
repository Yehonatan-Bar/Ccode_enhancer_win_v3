# Get Monitors Details

A utility tool for retrieving comprehensive information about all connected monitors/displays.

## Features

- Multi-monitor detection
- Display resolution information
- Monitor position coordinates
- Primary display identification
- DPI information (when available)
- JSON export functionality
- Comprehensive logging

## Usage

### Command Line
```bash
python get_monitors_detailes.py
```

### As a Module
```python
from get_monitors_detailes import get_display_info

# Get information about all monitors
displays = get_display_info()

for display in displays:
    print(f"Display {display['display_number']}:")
    print(f"  Resolution: {display['width']}x{display['height']}")
    print(f"  Position: ({display['x']}, {display['y']})")
    print(f"  Primary: {display['is_primary']}")
```

## Return Data Structure

Returns a list of dictionaries, each containing:

```python
{
    'display_number': 1,          # Sequential display number
    'width': 1920,               # Display width in pixels
    'height': 1080,              # Display height in pixels
    'x': 0,                      # X coordinate of display origin
    'y': 0,                      # Y coordinate of display origin
    'is_primary': True,          # Whether this is the primary display
    'name': 'Display 1',         # Display name (if available)
    'dpi': 96                    # DPI setting (if available)
}
```

## Output Files

The tool automatically saves display information to JSON files:
- Location: `display_info/display_info_YYYYMMDD_HHMMSS.json`
- Format: Pretty-printed JSON with 4-space indentation

## Example Output

### Console Output
```
=== Display Information ===

Display 1:
  display_number: 1
  width: 2560
  height: 1440
  x: 0
  y: 0
  is_primary: True
  name: DELL U2719D
  dpi: 109

Display 2:
  display_number: 2
  width: 1920
  height: 1080
  x: 2560
  y: 360
  is_primary: False
  name: ASUS VG248
  dpi: 96
```

### JSON Output
```json
[
    {
        "display_number": 1,
        "width": 2560,
        "height": 1440,
        "x": 0,
        "y": 0,
        "is_primary": true,
        "name": "DELL U2719D",
        "dpi": 109
    },
    {
        "display_number": 2,
        "width": 1920,
        "height": 1080,
        "x": 2560,
        "y": 360,
        "is_primary": false,
        "name": "ASUS VG248",
        "dpi": 96
    }
]
```

## Use Cases

1. **Multi-Monitor Setup Configuration**: Understand display arrangement
2. **Screenshot Tools**: Determine correct monitor for capture
3. **Window Positioning**: Calculate optimal window placement
4. **Display Diagnostics**: Verify monitor detection and settings
5. **Application Development**: Adapt UI for different display configurations

## Error Handling

- Graceful handling of display detection failures
- Comprehensive error logging
- Returns empty list on critical errors
- Platform information included in error logs

## System Information Logged

- Process ID
- Current working directory
- System platform
- Python version
- Timestamp of execution

## Requirements

- Python 3.7+
- `screeninfo` package

## Installation

```bash
pip install screeninfo
```

## Platform Support

- Windows
- macOS
- Linux

Note: Display name and DPI information availability may vary by platform.