import xml.etree.ElementTree as ET
import os
import sys
import logging
import traceback
import json

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

# Now we can import from Agents
from Agents.llms.llm_router import LLMRouter
from utils.extract_code_by_type.json_handler_extractor import extract_json
from logs.setup_logging import archive_existing_logs, setup_logging
from Agents.models import ElementIdentifierResponse
from Agents.agent_personas.conversation_manager import conversation_manager
from utils.click_html_element.clickable_elements_extractor import extract_clickable_elements



# Import logging setup
if __name__ == '__main__':
    from logs.setup_logging import archive_existing_logs, setup_logging
    from utils.extract_code_by_type.json_handler_extractor import extract_json
    from Agents.models import ElementIdentifierResponse
    from utils.click_html_element.clickable_elements_extractor import extract_clickable_elements

else:
    try:
        from logs.setup_logging import archive_existing_logs, setup_logging
        from utils.extract_code_by_type.json_handler_extractor import extract_json
        from Agents.models import ElementIdentifierResponse
        from utils.click_html_element.clickable_elements_extractor import extract_clickable_elements

    except ImportError:
        from logs.setup_logging import archive_existing_logs, setup_logging
        from utils.extract_code_by_type.json_handler_extractor import extract_json
        from Agents.models import ElementIdentifierResponse
        from utils.click_html_element.clickable_elements_extractor import extract_clickable_elements

# Load the config
with open('config.json', 'r') as f:
    config = json.load(f)

# Modify the log file name
config['logging']['log_file'] = os.path.basename(__file__).replace('.py', '.log')

# Setup logging
logs_dir = os.path.join(project_root, 'logs')
os.makedirs(logs_dir, exist_ok=True)
logger = setup_logging(config, __file__)


def construct_element_identifier_prompt(html: str, prompt: str, screenshot_path: str = None, display_info: dict = None, all_links: list = None) -> str:
    """
    Constructs an element identification prompt and processes it using conversation manager.
    If the JSON produced from extract_clickable_elements is longer than 10000 characters,
    it splits the processed content into chunks.
    """
    logger.info("=== Starting element identifier prompt construction ===")
    logger.info(f"User prompt: {prompt}")
    logger.info(f"HTML code length: {len(html)} characters")
    logger.info(f"Screenshot path: {screenshot_path}")
    logger.info(f"Display info: {display_info}")
    logger.info(f"Number of links: {len(all_links) if all_links else 0}")
    
    try:
        # Get the project root directory (Tools_Hub)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        logger.info(f"Project root directory: {project_root}")
        
        # Construct path to prompts.xml
        prompts_path = os.path.join(project_root, 'Agents', 'prompts.xml')
        logger.info(f"Loading prompts from: {prompts_path}")
        
        # Read and parse the XML file
        with open(prompts_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        logger.info("Successfully read prompts.xml file")
        root = ET.fromstring(xml_content)
        logger.info("Successfully parsed XML content")
        
        # Add logging for XML parsing
        logger.debug(f"XML content length: {len(xml_content)} characters")
        logger.debug("XML root element tags found:")
        for child in root:
            logger.debug(f"- {child.tag}")
        
        # Extract clickable elements first
        logger.info("Starting clickable elements extraction...")
        logger.debug(f"Display info being used: {json.dumps(display_info, indent=2)}")
        
        clickable_elements_full = extract_clickable_elements(
            html,
            display_info=display_info,
            all_links=all_links
        )
        
        logger.info(f"Number of clickable elements found: {len(clickable_elements_full)}")
        logger.debug("Sample of first few clickable elements:")
        for i, element in enumerate(clickable_elements_full[:3]):
            logger.debug(f"Element {i + 1}: {json.dumps(element, indent=2)}")
            
        filtered_html_full = json.dumps(clickable_elements_full, indent=4, ensure_ascii=False)
        logger.info(f"Extracted clickable elements JSON length: {len(filtered_html_full)} characters")
        
        # Get prefix templates from XML (using click_element key)
        prompt_prefix = root.find('.//click_element/click_element_prompt_prefix').text.strip()
        
        # Choose HTML and JSON prefixes based on the length of filtered_html_full
        if len(filtered_html_full) > 5000:
            html_prefix = root.find('.//click_element/click_element_partial_HTML_prefix').text.strip()
            json_prefix = root.find('.//click_element/click_element_partial_JSON_prefix').text.strip()
            logger.info("Using partial HTML prefixes due to large processed clickable elements content")
        else:
            html_prefix = root.find('.//click_element/click_element_HTML_prefix').text.strip()
            json_prefix = root.find('.//click_element/click_element_JSON_prefix').text.strip()
            logger.info("Using standard HTML prefixes")
            
        # Add logging for clickable elements extraction
        logger.info("Starting clickable elements extraction...")
        logger.debug(f"Display info being used: {json.dumps(display_info, indent=2)}")
        
        clickable_elements_full = extract_clickable_elements(
            html,
            display_info=display_info,
            all_links=all_links
        )
        
        logger.info(f"Number of clickable elements found: {len(clickable_elements_full)}")
        logger.debug("Sample of first few clickable elements:")
        for i, element in enumerate(clickable_elements_full[:3]):
            logger.debug(f"Element {i + 1}: {json.dumps(element, indent=2)}")
            
        filtered_html_full = json.dumps(clickable_elements_full, indent=4, ensure_ascii=False)
        logger.info(f"Extracted clickable elements JSON length: {len(filtered_html_full)} characters")
        logger.info(f"clickable_elements_full length: {len(clickable_elements_full)} characters")

        
        def process_chunk(filtered_html_full: str) -> str:
            logger.info("=== Starting chunk processing ===")
            logger.debug(f"Chunk length: {len(filtered_html_full)} characters")
            
            # Log prompt construction
            logger.debug(f"Prompt prefix length: {len(prompt_prefix)} characters")
            logger.debug(f"HTML prefix length: {len(html_prefix)} characters")
            logger.debug(f"JSON prefix length: {len(json_prefix)} characters")
            
            formatted_prompt = f"""
                {prompt_prefix}
                {prompt}
                {html_prefix}
                {filtered_html_full}
                {json_prefix}
            """
            
            logger.debug(f"Total formatted prompt length: {len(formatted_prompt)} characters")
            
            max_retries = 3
            retry_count = 0
            last_error = None
            
            while retry_count < max_retries:
                try:
                    logger.info(f"=== Processing attempt {retry_count + 1}/{max_retries} ===")
                    
                    llm_router = LLMRouter()
                    logger.info("Sending prompt to LLM Router...")
                    logger.debug(f"Prompt first 200 chars: {formatted_prompt[:200]}...")
                    
                    llm_response = llm_router.route_prompt(
                        prompt=formatted_prompt
                    )
                    
                    logger.info("LLM Router response received")
                    logger.debug(f"Response type: {type(llm_response)}")
                    
                    # Extract initial selector from LLM response
                    initial_selector = None
                    if isinstance(llm_response, dict):
                        if 'response' in llm_response and isinstance(llm_response['response'], dict):
                            initial_selector = llm_response['response'].get('selector')
                        elif 'selector' in llm_response:
                            initial_selector = llm_response['selector']
                    
                    logger.info(f"Initial selector from LLM: {initial_selector}")
                    
                    # Ensure llm_response is a string before slicing
                    if isinstance(llm_response, dict):
                        response_text = llm_response.get('content', '') or llm_response.get('message', '') or str(llm_response)
                        logger.info(f"LLM Response: {response_text[:700]}...")
                    else:
                        response_text = str(llm_response)
                        logger.info(f"LLM Response: {response_text[:700]}...")

                    # Save the initial model's response
                    initial_model_response = response_text
                    
                    # Combine the original prompt and LLM response
                    combined_prompt = f"""
                    {formatted_prompt}
                    
                    \nAssistant:
                    \n{response_text}
                    """
                    logger.info("Combined prompt created")
                    
                    # Send to conversation manager
                    logger.info("Sending to conversation manager")
                    result = conversation_manager(
                        conversation_name="find_HTML_element",
                        initial_prompt=combined_prompt
                    )
                    logger.info(f"Conversation manager response: {result}")
                    
                    # Check if the conversation manager returned an error or None response
                    if isinstance(result, dict):
                        content = result.get('content')
                        if content == 'None' or not content:
                            logger.info("Conversation manager returned None/empty response, falling back to initial selector")
                            if initial_selector:
                                return {'selector': initial_selector}
                            return "None"
                    
                    # Extract JSON from conversation manager response
                    try:
                        if isinstance(result, dict):
                            json_data = result
                        else:
                            json_data = extract_json(result)
                        
                        if not json_data:
                            logger.warning("No valid JSON found in conversation manager response")
                            if initial_selector:
                                return {'selector': initial_selector}
                            return "None"
                        
                        # Validate the JSON structure
                        if 'selector' not in json_data:
                            logger.warning("JSON missing required 'selector' field")
                            if initial_selector:
                                return {'selector': initial_selector}
                            return "None"
                        
                        return json_data['selector']
                        
                    except Exception as e:
                        logger.error(f"JSON processing error: {str(e)}")
                        if initial_selector:
                            return {'selector': initial_selector}
                        raise
                    
                except Exception as e:
                    logger.error(f"=== Error in attempt {retry_count + 1} ===")
                    logger.error(f"Error type: {type(e).__name__}")
                    logger.error(f"Error message: {str(e)}")
                    logger.debug(f"Full traceback:\n{traceback.format_exc()}")
                    last_error = e
                    retry_count += 1
                    
                    if retry_count < max_retries:
                        logger.info(f"Retrying... ({retry_count}/{max_retries})")
                    elif initial_selector:
                        logger.info("All retries failed, falling back to initial selector")
                        return {'selector': initial_selector}
            
            error_details = f"Error type: {last_error.__class__.__name__}, Message: {str(last_error)}"
            logger.error(f"Failed to process with conversation manager after {max_retries} attempts: {error_details}")
            return "None"
        
        # Save debug output files before processing chunks
        output_dir = os.path.join(project_root, 'debug_output')
        os.makedirs(output_dir, exist_ok=True)
        
        # Save clickable_elements_full
        elements_path = os.path.join(output_dir, 'clickable_elements_full.json')
        with open(elements_path, 'w', encoding='utf-8') as f:
            json.dump(clickable_elements_full, f, indent=4, ensure_ascii=False)
        logger.info(f"Saved clickable_elements_full to: {elements_path}")
        
        # Save filtered_html_full
        filtered_path = os.path.join(output_dir, 'filtered_html_full.json')
        with open(filtered_path, 'w', encoding='utf-8') as f:
            f.write(filtered_html_full)
        logger.info(f"Saved filtered_html_full to: {filtered_path}")

        # Process the extracted clickable elements content in chunks if needed
        if len(filtered_html_full) > 5000:
            logger.info("Processed clickable elements content exceeds 5000 characters, processing in chunks")
            chunk_size = 5000
            overlap = 500
            start = 0
            chunk_count = 0
            
            while start < len(filtered_html_full):
                chunk_count += 1
                end = min(start + chunk_size, len(filtered_html_full))
                chunk = filtered_html_full[start:end]
                
                logger.info(f"Processing chunk {chunk_count} from index {start} to {end}")
                result = process_chunk(chunk)
                logger.info(f"Chunk {chunk_count} result: {result}")
                
                if result != "None":
                    logger.info(f"Valid selector found in chunk {chunk_count}")
                    return result
                
                start = end - overlap
                logger.info(f"Moving to next chunk with overlap of {overlap} characters")
            
            logger.warning("No valid selector found in any chunk")
            return "None"
        else:
            logger.info("Processing entire processed clickable elements content at once")
            return process_chunk(filtered_html_full)
            
    except Exception as e:
        logger.error("=== Unexpected Error ===")
        logger.error("Failed to construct element identifier prompt")
        logger.error(f"Error type: {e.__class__.__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.info(f"Error traceback: {traceback.format_exc()}")
        return f"Error in element identification process: {e}"

if __name__ == '__main__':
    # Example usage
    sample_html = "<div id='content'><button>Click me</button></div>"
    sample_prompt = "Find the submit button in the main content area"
    sample_screenshot = r"C:\Users\yonzb\OneDrive\Documents\Ai_Projects\AI_Agents\Tools_Hub\screenshots\before_click\screenshot_20250210_220337_display_3.png"  # Optional
    result = construct_element_identifier_prompt(sample_html, sample_prompt, sample_screenshot)
    print(f"Identified selector: {result}")

#example outputs:
#{"selector": "a"}
#{"selector": "a[href='https://www.iana.org/domains/example']"}
