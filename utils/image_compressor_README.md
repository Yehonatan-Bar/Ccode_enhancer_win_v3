# Image Compressor

A utility tool for compressing multiple image files into a single ZIP archive with comprehensive logging.

## Features

- Multiple image compression into ZIP archives
- File existence verification
- Detailed file statistics logging
- Permission error handling
- Timestamp-based file information
- Compression verification

## Usage

### Command Line
```python
# Modify the example in the script's main section
image_paths = [
    r"C:\path\to\image1.jpg",
    r"C:\path\to\image2.png",
    r"C:\path\to\image3.gif"
]
output_zip = r"C:\path\to\compressed_images.zip"

python image_compressor.py
```

### As a Module
```python
from image_compressor import compress_images

# List of images to compress
images = [
    "photo1.jpg",
    "screenshot.png",
    "diagram.gif",
    "logo.bmp"
]

# Compress images
success = compress_images(
    image_paths=images,
    output_path="archive.zip"
)

if success:
    print("Compression successful!")
else:
    print("Compression failed!")
```

## Parameters

- `image_paths` (List[str]): List of absolute or relative paths to image files
- `output_path` (str): Path where the ZIP archive will be created

## Return Value

- `bool`: True if compression was successful, False otherwise

## File Statistics Logged

For each image file:
- File size in bytes (with comma formatting)
- Last modified timestamp
- File permissions (octal format)

For the output ZIP:
- Final archive size
- Creation timestamp

## Supported Image Formats

The tool can compress any file type, but is intended for images:
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- TIFF (.tif, .tiff)
- WebP (.webp)
- SVG (.svg)

## Error Handling

### FileNotFoundError
Raised when any specified image file doesn't exist:
```python
FileNotFoundError: Image file not found: C:\path\to\missing.jpg
```

### PermissionError
Raised when:
- No read permission for input images
- No write permission for output directory
- File is locked by another process

### General Exceptions
All other errors are caught and logged with:
- Error type
- Error message
- Full traceback
- System information
- Python version

## Example Log Output

```
2024-01-15 10:30:45 - INFO - === Starting image compression operation ===
2024-01-15 10:30:45 - INFO - Number of images to compress: 3
2024-01-15 10:30:45 - INFO - Output zip file: compressed_images.zip
2024-01-15 10:30:45 - INFO - === Image File Statistics: image1.jpg ===
2024-01-15 10:30:45 - INFO - File size: 2,457,891 bytes
2024-01-15 10:30:45 - INFO - Last modified: 2024-01-10 14:23:15
2024-01-15 10:30:46 - INFO - === Zip Archive Statistics ===
2024-01-15 10:30:46 - INFO - File size: 7,234,567 bytes
2024-01-15 10:30:46 - INFO - === Image compression operation completed successfully ===
```

## ZIP Archive Structure

The compressed images are stored in the ZIP with their basename only:
```
archive.zip
├── image1.jpg
├── image2.png
└── image3.gif
```

Original directory structure is not preserved.

## Use Cases

1. **Batch Image Archiving**: Compress multiple images for storage
2. **Email Attachments**: Create single archive for multiple images
3. **Backup Operations**: Archive image collections
4. **Web Upload**: Prepare multiple images as single file
5. **Space Saving**: Reduce storage usage for image collections

## Performance Considerations

- No image recompression (stores original quality)
- ZIP compression depends on image format
- Already compressed formats (JPEG) see minimal size reduction
- Uncompressed formats (BMP, TIFF) see significant reduction

## Requirements

- Python 3.7+
- Standard library only (no external dependencies)

## Platform Compatibility

- Windows
- macOS  
- Linux

Note: File paths should use appropriate separators for the platform.