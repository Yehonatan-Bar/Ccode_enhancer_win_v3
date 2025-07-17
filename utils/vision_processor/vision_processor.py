import os
import base64
from groq import Groq
from typing import Optional
import sys
import json

# Correctly determine project_root (three levels up from vision_processor.py)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root) # Append project_root to sys.path
from logs.setup_logging import setup_logging

config_path = os.path.join(project_root, 'config.json')
with open(config_path, 'r') as f:
    config = json.load(f)
config['logging']['log_file'] = os.path.basename(__file__).replace('.py', '.log')
logger = setup_logging(config, __file__)

def _encode_image(image_path: str) -> str:
    """Encode local image to base64 string."""
    logger.debug(f"Encoding image from path: {image_path}")
    try:
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode('utf-8')
            logger.debug("Image successfully encoded to base64")
            return encoded
    except Exception as e:
        logger.error(f"Failed to encode image: {str(e)}")
        raise

def vision_processor(
    image_path: str,
    prompt: Optional[str] = None,
    question: str = "Give me a detailed description of the image, including the text and any other details and elements.",
    is_url: bool = False,
    api_key: Optional[str] = None,
    temperature: float = 0.5,
    max_tokens: int = 4094
) -> str:
    """
    Process an image and return the model's response.
    Args:
        image_path (str): Path to the image file or URL
        prompt (Optional[str]): Custom prompt to use with the image
        question (str): Question to ask about the image if no prompt is provided
        is_url (bool): Whether the image_path is a URL
        api_key (Optional[str]): GROQ API key. If None, uses environment variable
        temperature (float): Sampling temperature
        max_tokens (int): Maximum tokens for the response
    Returns:
        str: The model's response describing the image
    """
    logger.info(f"Processing image. Path: {image_path}, Is URL: {is_url}")
    logger.debug(f"Parameters - Question: {question}, Temperature: {temperature}, Max Tokens: {max_tokens}")
    try:
        # If api_key is not supplied, fetch from environment
        if not api_key:
            env_key = os.getenv("GROQ_API_KEY")
            if not env_key:
                raise ValueError(
                    "No API key found. Please set the GROQ_API_KEY environment "
                    "variable or pass the api_key argument."
                )
            api_key = env_key
        client = Groq(api_key=api_key)
        model = "meta-llama/llama-4-maverick-17b-128e-instruct"
        logger.debug(f"Using model: {model}")
        # Prepare the image URL based on whether it's a local file or URL
        if is_url:
            logger.debug("Using direct URL for image")
            image_url = image_path
        else:
            logger.debug("Encoding local image file")
            base64_image = _encode_image(image_path)
            image_url = f"data:image/jpeg;base64,{base64_image}"
        # Use prompt if provided, otherwise use question
        user_text = prompt if prompt is not None else question
        logger.debug("Creating completion request")
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_text
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=1,
            stream=False,
            stop=None
        )
        response = completion.choices[0].message.content
        logger.info("Successfully processed image and received response")
        logger.debug(f"Response length: {len(response)} characters")
        return response
    except Exception as e:
        logger.error(f"Error in process_image_with_vision: {str(e)}")
        raise

# Example usage if run directly
if __name__ == "__main__":
    try:
        result = vision_processor(
            image_path=r"C:\Users\yonzb\OneDrive\Documents\Ai_Projects\AI_Agents\Tools_Hub\screenshots\screenshot_1748450714.png",
            question="What objects can you see in this image?"
        )
        print(result)
    except Exception as e:
        print(f"Error: {str(e)}")