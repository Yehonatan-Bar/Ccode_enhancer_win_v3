# Vision Processor

An AI-powered image analysis tool using GROQ API with Llama vision models for detailed image understanding and description.

## Features

- Local image file analysis
- URL-based image analysis
- Base64 encoding for local images
- Customizable prompts and questions
- Temperature and token control
- Comprehensive error handling
- Detailed logging

## Installation

```bash
pip install groq
```

## Configuration

### API Key Setup

Set the GROQ API key as an environment variable:

```bash
# Windows
set GROQ_API_KEY=your-api-key-here

# macOS/Linux
export GROQ_API_KEY=your-api-key-here
```

Alternatively, pass the API key directly when initializing.

## Usage

### As a Module

```python
from vision_processor import process_image_with_vision

# Analyze local image with default question
result = process_image_with_vision(
    image_path="screenshot.png"
)

# Analyze with custom question
result = process_image_with_vision(
    image_path="screenshot.png",
    question="What UI elements are visible in this screenshot?"
)

# Analyze with custom prompt (overrides question)
result = process_image_with_vision(
    image_path="screenshot.png",
    prompt="Describe the color scheme and layout of this interface"
)

# Analyze image from URL
result = process_image_with_vision(
    image_path="https://example.com/image.jpg",
    is_url=True,
    question="What objects are in this image?"
)

# With custom API key
result = process_image_with_vision(
    image_path="image.png",
    api_key="your-groq-api-key"
)
```

### Direct Class Usage

```python
from vision_processor import VisionProcessor

# Initialize processor
processor = VisionProcessor(api_key="optional-api-key")

# Process image with full control
response = processor.process_image(
    image_path="image.png",
    prompt="Analyze this image",
    question="What do you see?",
    is_url=False,
    temperature=0.5,
    max_tokens=4094
)
```

## Parameters

### process_image_with_vision()

- `image_path` (str): Path to local image file or URL
- `prompt` (Optional[str]): Custom prompt (overrides question)
- `question` (str): Question about the image (default: detailed description request)
- `is_url` (bool): Whether image_path is a URL (default: False)
- `api_key` (Optional[str]): GROQ API key (uses env variable if not provided)

### VisionProcessor.process_image()

- `image_path` (str): Path to local image file or URL
- `prompt` (Optional[str]): Custom prompt (overrides question)
- `question` (str): Question about the image
- `is_url` (bool): Whether image_path is a URL
- `temperature` (float): Model temperature (0-1, default: 0.5)
- `max_tokens` (int): Maximum response tokens (default: 4094)

## Model Information

- Model: `meta-llama/llama-4-maverick-17b-128e-instruct`
- Provider: GROQ API
- Capabilities: Advanced vision understanding and natural language generation

## Example Responses

### UI Analysis
```
The screenshot shows a modern web interface with a dark theme. The navigation bar 
at the top contains a logo on the left and menu items including "Home", "Products", 
"About", and "Contact". The main content area features a hero section with a large 
heading "Welcome to Our Platform" in white text against a gradient background...
```

### Object Detection
```
In this image, I can identify the following objects:
1. A red bicycle leaning against a brick wall
2. A potted plant with green leaves to the right of the bicycle
3. A wooden bench in the background
4. Street lamp visible in the upper right corner
The scene appears to be in an urban setting during daytime...
```

## Error Handling

The tool handles various error scenarios:

- Missing API key
- Invalid image path
- Network errors for URL images
- API request failures
- Image encoding errors

All errors are logged with detailed information for debugging.

## Logging

Comprehensive logging includes:
- Image processing start/end
- Encoding operations
- API request details
- Response metadata
- Error information with stack traces

## Use Cases

1. **Accessibility Testing**: Describe UI elements for screen readers
2. **Content Moderation**: Analyze images for inappropriate content
3. **Documentation**: Auto-generate image descriptions
4. **Quality Assurance**: Verify UI elements in screenshots
5. **Data Extraction**: Extract text and information from images
6. **Visual Search**: Identify objects and scenes in images

## Best Practices

1. **Image Quality**: Use clear, high-resolution images for best results
2. **Specific Questions**: Ask targeted questions for more useful responses
3. **Rate Limiting**: Be mindful of API rate limits
4. **Error Handling**: Always handle potential errors in production
5. **Caching**: Consider caching responses for repeated images

## Supported Image Formats

- JPEG/JPG
- PNG
- GIF
- BMP
- WebP
- Most common image formats

## Performance Considerations

- Local images are base64 encoded (increases size by ~33%)
- Large images may take longer to process
- API response time varies with prompt complexity
- Temperature affects response consistency

## Security Notes

- API keys should never be hardcoded
- Use environment variables for production
- Be cautious with sensitive images
- Consider data privacy when using cloud APIs