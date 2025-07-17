from hashlib import scrypt
import json
import time
import sys
import os
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# Adjust the path to the logs/setup_logging.py if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from logs.setup_logging import setup_logging

# Load config and setup logging
with open('config.json', 'r') as f:
    config = json.load(f)

logger = setup_logging(config, 'fetch_resource_details')

def get_resource_details(page_url, resource_url):
    logger.info(f"Starting resource detail analysis for page: {page_url}")
    logger.info(f"Target resource: {resource_url}")

    # Setup Chrome options and performance logging
    logger.debug("Setting up Chrome options and capabilities")
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')

    # Enable performance logging
    caps = DesiredCapabilities.CHROME.copy()
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    logger.debug("Initializing Chrome WebDriver with performance logging")
    driver = webdriver.Chrome(options=chrome_options)

    # Enable Network logging via CDP
    driver.execute_cdp_cmd("Network.enable", {})
    logger.debug("CDP Network monitoring enabled")

    # A dictionary to store request and response info by requestId
    requests_data = {}

    def on_request_will_be_sent(params):
        request = params.get("request", {})
        url = request.get("url")
        request_id = params.get("requestId")
        if url:
            logger.debug(f"Request intercepted - ID: {request_id}, URL: {url}")
            requests_data[request_id] = {
                "url": url,
                "request_headers": request.get("headers", {}),
                "method": request.get("method"),
                "request_post_data": request.get("postData", None),
            }

    def on_request_headers_extra_info(params):
        request_id = params.get("requestId")
        if request_id in requests_data:
            extra_headers = params.get("headers", {})
            requests_data[request_id]["request_headers"].update(extra_headers)

    def on_response_received(params):
        response = params.get("response", {})
        request_id = params.get("requestId")
        if request_id in requests_data:
            requests_data[request_id]["status"] = response.get("status")
            requests_data[request_id]["status_text"] = response.get("statusText")
            requests_data[request_id]["mimeType"] = response.get("mimeType")
            requests_data[request_id]["response_headers"] = response.get("headers", {})

    def on_response_headers_extra_info(params):
        request_id = params.get("requestId")
        if request_id in requests_data:
            extra_headers = params.get("headers", {})
            if "response_headers" not in requests_data[request_id]:
                requests_data[request_id]["response_headers"] = {}
            requests_data[request_id]["response_headers"].update(extra_headers)

    def cdp_event_listener(method, params):
        event_handlers = {
            'Network.requestWillBeSent': on_request_will_be_sent,
            'Network.requestWillBeSentExtraInfo': on_request_headers_extra_info,
            'Network.responseReceived': on_response_received,
            'Network.responseReceivedExtraInfo': on_response_headers_extra_info
        }
        if method in event_handlers:
            event_handlers[method](params)

    logger.info(f"Loading page: {page_url}")
    driver.get(page_url)
    logger.debug("Waiting for resources to load...")
    time.sleep(5)

    # Retrieve performance logs
    logger.debug("Retrieving performance logs")
    try:
        perf_logs = driver.get_log('performance')
        logger.info(f"Retrieved {len(perf_logs)} performance log entries")
    except Exception as e:
        logger.error(f"Failed to retrieve performance logs: {e}")
        driver.quit()
        print("Could not retrieve performance logs.")
        return

    # Process performance logs to extract CDP network events
    logger.debug("Processing performance logs")
    for entry in perf_logs:
        try:
            log_msg = json.loads(entry['message'])
            message = log_msg.get('message', {})
            method = message.get('method')
            params = message.get('params', {})
            if method and params and method.startswith("Network."):
                logger.debug(f"Processing CDP event: {method}")
                cdp_event_listener(method, params)
        except Exception as e:
            logger.error(f"Error processing log entry: {str(e)}")

    # Find target resource
    logger.debug("Searching for target resource in collected data")
    target_request_id = None
    for req_id, data in requests_data.items():
        if data.get("url") == resource_url:
            target_request_id = req_id
            logger.info(f"Found target resource - Request ID: {req_id}")
            break

    if not target_request_id:
        logger.warning("Target resource not found in network logs")
        driver.quit()
        print("Resource not found in network logs.")
        return

    # Get response body for the target resource
    logger.debug("Attempting to retrieve response body")
    try:
        body_data = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": target_request_id})
        response_body = body_data.get("body", "")
        logger.info("Successfully retrieved response body")
    except Exception as e:
        logger.warning(f"Failed to retrieve response body: {str(e)}")
        response_body = None

    # Print results
    resource_details = requests_data[target_request_id]
    print("=== General Information ===")
    print(f"URL: {resource_details.get('url')}")
    print(f"Status: {resource_details.get('status')} {resource_details.get('status_text')}")
    print(f"MIME Type: {resource_details.get('mimeType')}")

    print("\n=== Request Headers ===")
    for k, v in resource_details.get("request_headers", {}).items():
        print(f"{k}: {v}")

    if resource_details.get("request_post_data"):
        print("\n=== Request Payload ===")
        print(resource_details.get("request_post_data"))

    print("\n=== Response Headers ===")
    for k, v in resource_details.get("response_headers", {}).items():
        print(f"{k}: {v}")

    if response_body is not None:
        print("\n=== Response Body ===")
        print(response_body)

    logger.info("Resource detail analysis completed")
    driver.quit()

if __name__ == "__main__":
    logger.info("Starting fetch_resource_details script")
    if len(sys.argv) < 3:
        logger.error("Insufficient arguments provided")
        print("Usage: python get_resource_details.py <page_url> <resource_url>")
        sys.exit(1)

    page_url = sys.argv[1]
    resource_url = sys.argv[2]
    get_resource_details(page_url, resource_url)


# **Script Overview**

# This script is designed to analyze the network activity of a given webpage and extract detailed information about a specific resource request made by the page. It leverages Selenium’s Chrome WebDriver and the Chrome DevTools Protocol (CDP) to capture network events and logs, enabling deep inspection into requests and responses associated with the page.

# **What the Script Does**

# 1. **Page Loading & Monitoring:**  
#    The script navigates to a specified webpage using a headless Chrome browser instance. Once the page is loaded, it waits briefly to ensure that most resources have been requested and received.

# 2. **Network Event Capturing via CDP:**  
#    After enabling the Chrome DevTools Protocol’s Network domain, the script listens for a series of network-related events (e.g., `Network.requestWillBeSent`, `Network.responseReceived`). These events provide insights into:
#    - Outgoing HTTP requests (URLs, methods, request headers, and payloads).
#    - Incoming HTTP responses (status codes, headers, MIME types).
   
# 3. **Performance Log Retrieval & Processing:**  
#    The script retrieves "performance" logs from the browser, which contain raw CDP events. It filters and processes these logs to reconstruct a mapping of request IDs to their associated request and response data. This allows identifying which request corresponds to the target resource you are interested in.

# 4. **Identifying the Target Resource:**  
#    Using the URL of the target resource (e.g., a CSS, JavaScript, or API endpoint), the script searches through the collected request-response pairs. Once found, it:
#    - Extracts request details (URL, headers, and if applicable, POST data).
#    - Extracts response details (status, status text, MIME type, response headers).
#    - Attempts to retrieve and display the response body content of the resource.

# **What the Script Returns**

# - **Console Output:**
#   - **General Information:**  
#     Prints the resource’s URL, HTTP status code, status text, and MIME type.
  
#   - **Request Headers:**  
#     Displays the headers that were sent with the HTTP request.
  
#   - **Request Payload (if any):**  
#     If the request included POST data (such as form inputs or JSON), it prints out that payload.
  
#   - **Response Headers:**  
#     Prints the headers returned by the server in response to the request.
  
#   - **Response Body:**  
#     If available, the script retrieves and prints the full response body of the requested resource (e.g., HTML, JSON, CSS, JavaScript code).

# - **Logs:**  
#   The script also logs its progress and any issues encountered to a specified log file. These logs are helpful for troubleshooting and verifying the workflow.

# **Use Cases**

# - **Resource Inspection for Debugging:**  
#   Developers can use this script to debug resource loading issues on a webpage, such as incorrect response headers or unexpected request payloads.
  
# - **API Monitoring:**  
#   For pages making AJAX calls, the script can capture the request and response cycles to understand the data exchange between the front-end and the back-end.

# - **Performance Analysis:**  
#   By examining request and response headers, one can gain insights into caching headers, compression, and other performance-related parameters.

# **In Summary**

# This scrypt automates a headless Chrome browser to load a webpage and capture detailed information about a specified resource request. It returns a comprehensive console output of request and response details, making it a powerful tool for web developers, QA engineers, and site administrators who need to inspect and troubleshoot network activity at a granular level.