import logging
import os
import sys

# Point to the actual root directory of your project
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from typing import Optional
from utils.llama_3_3_70b import get_llama_response

def get_element_id(element_description: str, html_content: str, custom_prompt: Optional[str] = None) -> str:
    """
    Get the element identifier based on description and HTML content using LLM.
    
    Args:
        element_description (str): Description of the element to be clicked
        html_content (str): HTML content of the page
        custom_prompt (str, optional): Custom prompt for the language model
        
    Returns:
        str: Element identifier from LLM response
    """
    
    # Default prompt if none provided
    default_prompt = """
    Given the HTML content below and the description of an element, 
    identify and return ONLY the ID of the element that best matches the description.
    If no ID is available, return a unique CSS selector that can identify the element.
    
    Description of the element: {description}
    
    HTML Content:
    {html}
    
    Return only the ID or selector, nothing else.
    """
    
    # Use custom prompt if provided, otherwise use default
    prompt_template = custom_prompt if custom_prompt else default_prompt
    
    # Format the prompt with the provided information
    final_prompt = prompt_template.format(
        description=element_description,
        html=html_content
    )
    
    # Get response from LLama model
    element_id = get_llama_response(final_prompt)
    
    return element_id.strip()

if __name__ == "__main__":
    # Example HTML content
    example_html = """
    <div class="container">
        <button id="submit-btn" class="primary-button">Submit Form</button>
        <div id="user-profile" class="profile-section">
            <h2>User Profile</h2>
            <a href="#" id="edit-profile">Edit Profile</a>
        </div>
    </div>
    """
    
    # Example element description
    description = "the submit button"
    
    try:
        # Get the element identifier
        result = get_element_id(description, example_html)
        print(f"Description: '{description}'")
        print(f"Found identifier: '{result}'")
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
